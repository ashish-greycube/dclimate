# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,get_link_to_form,get_datetime,getdate,get_time
from frappe import _
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.model.mapper import get_mapped_doc
from erpnext import get_company_currency, get_default_company
from frappe.utils import getdate, cstr, flt

class DCCampaignCompletionForm(Document):
	def on_submit(self):
		if not self.completion_date_time:
			frappe.throw(msg=_("Please enter <b>Completion Date Time</b> value"),title="Missing Completion Date Time.")	
		frappe.db.set_value("DC Campaign Completion Form", self.name, 'status', 'In Progress')
		if len(self.get("job_codes")) == 0:
			frappe.msgprint(_("No Job Codes exists , hence Purchase Invoice <b>not</b> created."))			
		else:
			purchase_invoice=make_purchase_invoice(self.name)
			if purchase_invoice!=0:
				self.purchase_invoice=purchase_invoice
				frappe.db.set_value("DC Campaign Completion Form", self.name, "purchase_invoice", purchase_invoice)
				frappe.msgprint(msg=_("Purchase Invoice {0} is created based on DC Campaign Completion Form {1}"
				.format(frappe.bold(get_link_to_form("Purchase Invoice",purchase_invoice)),frappe.bold(self.name))),
				title="Purchase Invoice is created.",
				indicator="green")

		if len(self.get("parts_detail")) == 0:
			frappe.msgprint(_("No Parts Detail exists, hence Stock Entry <b>not</b> created."))
		else:
			stock_entry=make_stock_entry(self.name)

			if stock_entry!=0:
				self.material_issue=stock_entry
				frappe.db.set_value("DC Campaign Completion Form", self.name, "material_issue", stock_entry)
				frappe.msgprint(msg=_("Material Issue {0} is created based on DC Campaign Completion Form {1}"
				.format(frappe.bold(get_link_to_form("Stock Entry",stock_entry)),frappe.bold(self.name))),
				title="Stock Entry is created.",
				indicator="green")			

	def validate(self):
		self.calculate_total_srt_values()

	def calculate_total_srt_values(self):
		# validate job price is present in supplier and calculate total hours and cost
		total_srt_hours=0
		total_srt_cost=0
		if self.service_by_supplier:
			per_hour_rate_cf = frappe.db.get_value('Supplier', self.service_by_supplier, 'per_hour_rate_cf')
			if not per_hour_rate_cf:
				frappe.throw(msg=_('Per hour job rate is not defined for supplier {0}. Please contact DClimate'.format(frappe.bold(get_link_to_form('Supplier',self.service_by_supplier)))),title="Missing per hour job rate for supplier.")
		if self.job_codes:
			for job_item in self.job_codes:
				if job_item.job_code and self.service_by_supplier:
					total_srt_cost=total_srt_cost+job_item.hours*per_hour_rate_cf
				if job_item.hours:
					total_srt_hours=total_srt_hours+job_item.hours
			self.total_srt_hours=total_srt_hours
			self.total_srt_cost=total_srt_cost

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
		doc = frappe.get_doc('DC Campaign Completion Form', source_name)
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.purpose = "Material Issue"
		stock_entry.set_stock_entry_type()
		stock_entry.from_warehouse = doc.default_parts_issue_warehouse
		stock_entry.company = get_default_company()
		stock_entry.remarks = _(" It is created from DC Campaign Completion Form {0}").format(doc.name)
		cost_center = frappe.get_cached_value("Company", get_default_company(), "cost_center")
		expense_account = frappe.db.get_single_value('DClimate Settings', 'warranty_repair_account')

		for entry in doc.parts_detail:
			se_child = stock_entry.append("items")
			se_child.item_code = entry.item
			se_child.item_name = frappe.db.get_value("Item", entry.item, "item_name")
			se_child.uom = frappe.db.get_value("Item", entry.item, "stock_uom")
			se_child.stock_uom = se_child.uom
			se_child.qty = flt(entry.qty)
			# in stock uom
			se_child.conversion_factor = 1
			se_child.cost_center = cost_center
			se_child.expense_account = expense_account

		stock_entry.save(ignore_permissions=True)
		return stock_entry.name

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	
	doc = frappe.get_doc('DC Campaign Completion Form', source_name)

	def set_missing_values(source, target):
		per_hour_rate_cf = frappe.db.get_value('Supplier', source.service_by_supplier, 'per_hour_rate_cf')
		target.status='Draft'
		target.set_posting_time=1
		target.posting_date=getdate(source.completion_date_time)
		target.posting_time=get_time(source.completion_date_time)
		target.contact_person=get_default_contact('Supplier',source.service_by_supplier)

		for item in source.job_codes:
			target.append('items',{
			"item_code":item.job_code,
			"qty" :item.hours,
			"rate":per_hour_rate_cf
			})

		doc = frappe.get_doc(target)
		doc.bill_no = source.name
		doc.run_method("set_missing_values")
		doc.run_method("calculate_taxes_and_totals")

	doclist = get_mapped_doc("DC Campaign Completion Form", source_name,	{
		"DC Campaign Completion Form": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"service_by_supplier":"supplier",
  			"received_date": "bill_date" ,
				"completion_date":"posting_date"
			},
			"validation": {
				"docstatus": ["=", 1],
			},
		}
	}, target_doc, set_missing_values,ignore_permissions=True)
	doclist.save(ignore_permissions=True)
	return doclist.name		

def change_dc_campaign_completion_status_to_finished(self,method):
	if self.doctype=='Purchase Invoice':
		dc_campaign_list=frappe.db.get_list('DC Campaign Completion Form', 
										filters={'purchase_invoice': ['=', self.name]},
										fields=['name','status', 'purchase_invoice','material_issue'])
		if len(dc_campaign_list)>0:
			dc_campaign_name=dc_campaign_list[0].name
			dc_campaign_status=dc_campaign_list[0].status
			if dc_campaign_status!='Finished':
				dc_campaign_material_issue=dc_campaign_list[0].get('material_issue') or None
				if dc_campaign_material_issue:
					material_issue_docstatus = frappe.db.get_value('Stock Entry', dc_campaign_material_issue, 'docstatus')	
					if material_issue_docstatus==1:
						frappe.db.set_value('DC Campaign Completion Form', dc_campaign_name, 'status', 'Finished')		
						frappe.msgprint(msg=_("DC Campaign Completion Form {0} status is changed to <b>Finished</b>. <br> As associated Purchase Invoice {1} and Material Issue {2} are in submitted state."
						.format(frappe.bold(get_link_to_form("DC Campaign Completion Form",dc_campaign_name)),frappe.bold(self.name),frappe.bold(dc_campaign_material_issue))),
						title="DC Campaign Completion Form status changed.",
						indicator="green")
					else:
						frappe.msgprint(msg=_("DC Campaign Completion Form {0} status is not changed to <b>Finished</b>. <br> As associated Material Issue {1} is not in submitted state."
						.format(frappe.bold(get_link_to_form("DC Campaign Completion Form",dc_campaign_name)),frappe.bold(dc_campaign_material_issue))),
						title="DC Campaign Completion Form status not changed.",
						indicator="orange")
				else:
					frappe.db.set_value('DC Campaign Completion Form', dc_campaign_name, 'status', 'Finished')		
					frappe.msgprint(msg=_("DC Campaign Completion Form {0} status is changed to <b>Finished</b>. <br> As associated Purchase Invoice {1} is in submitted state."
					.format(frappe.bold(get_link_to_form("DC Campaign Completion Form",dc_campaign_name)),frappe.bold(self.name))),
					title="DC Campaign Completion Form status changed.",
					indicator="green")							
	elif self.doctype=='Stock Entry':
		dc_campaign_list=frappe.db.get_list('DC Campaign Completion Form', 
										filters={'material_issue': ['=', self.name]},
										fields=['name','status', 'purchase_invoice','material_issue'])
		if len(dc_campaign_list)>0:
			dc_campaign_name=dc_campaign_list[0].name
			dc_campaign_status=dc_campaign_list[0].status
			if dc_campaign_status!='Finished':
				dc_campaign_purchase_invoice=dc_campaign_list[0].get('purchase_invoice') or None
				if dc_campaign_purchase_invoice:
					purchase_invoice_docstatus = frappe.db.get_value('Purchase Invoice', dc_campaign_purchase_invoice, 'docstatus')	
					if purchase_invoice_docstatus==1:
						frappe.db.set_value('DC Campaign Completion Form', dc_campaign_name, 'status', 'Finished')		
						frappe.msgprint(msg=_("DC Campaign Completion Form {0} status is changed to <b>Finished</b>. <br> As associated Purchase Invoice {1} and Material Issue {2} are in submitted state."
						.format(frappe.bold(get_link_to_form("DC Campaign Completion Form",dc_campaign_name)),frappe.bold(self.name),frappe.bold(dc_campaign_purchase_invoice))),
						title="DC Campaign Completion Form status changed.",
						indicator="green")
					else:
						frappe.msgprint(msg=_("DC Campaign Completion Form {0} status is not changed to <b>Finished</b>. <br> As associated Purchase Invoice {1} is not in submitted state."
						.format(frappe.bold(get_link_to_form("DC Campaign Completion Form",dc_campaign_name)),frappe.bold(dc_campaign_purchase_invoice))),
						title="DC Campaign Completion Form status not changed.",
						indicator="orange")
				else:
					#  This case will not happen
					frappe.db.set_value('DC Campaign Completion Form', dc_campaign_name, 'status', 'Finished')		
					frappe.msgprint(msg=_("DC Campaign Completion Form {0} status is changed to <b>Finished</b>. <br> As associated Material Issue {1} is in submitted state."
					.format(frappe.bold(get_link_to_form("DC Campaign Completion Form",dc_campaign_name)),frappe.bold(self.name))),
					title="DC Campaign Completion Form status changed.",
					indicator="green")
	