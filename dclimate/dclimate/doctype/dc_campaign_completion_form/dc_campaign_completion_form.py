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
			frappe.throw(msg=_("Please make status as <b>Finished</b> and enter <b>Completion Date Time</b> value"),title="Missing Completion Date Time.")	
		purchase_invoice=make_purchase_invoice(self.name)
		if purchase_invoice!=0:
			self.purchase_invoice=purchase_invoice
			frappe.db.set_value("DC Campaign Completion Form", self.name, "purchase_invoice", purchase_invoice)
			frappe.msgprint(msg=_("Purchase Invoice {0} is created based on DC Campaign Completion Form {1}"
			.format(frappe.bold(get_link_to_form("Purchase Invoice",purchase_invoice)),frappe.bold(self.name))),
			title="Purchase Invoice is created.",
			indicator="green")

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
		# validate job price is present in supplier price list and calculate total hours and cost
		total_srt_hours=0
		total_srt_cost=0
		# supplier_price_list=self.supplier_price_list
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
		
		# validate repair part price is present in buy back price list
		default_parts_under_warranty_replacement_service_item=frappe.db.get_single_value('DClimate Settings', 'default_parts_under_warranty_replacement_service_item')
		parts_buy_back_margin_price_list=frappe.db.get_single_value('DClimate Settings', 'parts_buy_back_margin_price_list')
		warranty_replacement_service_item_rate=0
		for item in self.parts_detail:
			replacement_service_item_rate=frappe.db.get_all('Item Price', filters={
																		'price_list': ['=', parts_buy_back_margin_price_list],
																		'item_code': ['=', item.item]
																		}, fields='price_list_rate')
			if not replacement_service_item_rate:
				frappe.throw(msg=_("Item price for part no {0} not found in parts buy back price list {1}. Please contact DClimate"
						.format(frappe.bold(item.item),frappe.bold(parts_buy_back_margin_price_list))),title='Repair part price not found error.')	
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
	
	# from erpnext.accounts.party import get_payment_terms_template

	doc = frappe.get_doc('DC Campaign Completion Form', source_name)
	# if doc.parts_warranty_status!='Under Warranty' and doc.labor_warranty_status!='Under Warranty':
	if doc.labor_warranty_status!='Under Warranty':		
		frappe.msgprint(msg=_("Labour warranty status is {0}. Hence there are <b>no items</b> to create a Purchase Invoice."
				.format(frappe.bold(doc.labor_warranty_status)))
				,title='Purchase Invoice is not created.',indicator="yellow")	
		return 0	

	# prepare single item and price for repair parts
	# default_parts_under_warranty_replacement_service_item=frappe.db.get_single_value('DClimate Settings', 'default_parts_under_warranty_replacement_service_item')
	# parts_buy_back_margin_price_list=frappe.db.get_single_value('DClimate Settings', 'parts_buy_back_margin_price_list')
	# warranty_replacement_service_item_rate=0
	# if doc.parts_warranty_status=='Under Warranty':
	# 	for item in doc.parts_detail:
	# 		replacement_service_item_rate=frappe.db.get_all('Item Price', filters={
	# 																	'price_list': ['=', parts_buy_back_margin_price_list],
	# 																	'item_code': ['=', item.item]
	# 																	}, fields='price_list_rate')
	# 		if replacement_service_item_rate:
	# 			replacement_service_item_rate=replacement_service_item_rate[0].price_list_rate
	# 		else:
	# 			frappe.throw(msg=_("Item price for part no {0} not found in parts buy back price list {1}. Please contact DClimate"
	# 					.format(frappe.bold(item.item),frappe.bold(parts_buy_back_margin_price_list))),title='Repair part price not found error.')
	# 		warranty_replacement_service_item_rate+=replacement_service_item_rate*item.qty															

	def set_missing_values(source, target):
		per_hour_rate_cf = frappe.db.get_value('Supplier', source.service_by_supplier, 'per_hour_rate_cf')
		target.status='Draft'
		target.set_posting_time=1
		target.posting_date=getdate(source.completion_date_time)
		target.posting_time=get_time(source.completion_date_time)
		target.contact_person=get_default_contact('Supplier',source.service_by_supplier)
		# target.dc_service_record_cf=source.name

		# if source.parts_detail and len(source.parts_detail)>0:
		# 	if source.parts_warranty_status=='Under Warranty':
		# 		target.append('items',{
		# 		"item_code":default_parts_under_warranty_replacement_service_item,
		# 		"qty" :1,
		# 		"rate":warranty_replacement_service_item_rate				
		# 		})

		if source.labor_warranty_status=='Under Warranty':
			for item in source.job_codes:
				target.append('items',{
				"item_code":item.job_code,
				"qty" :item.hours,
				"rate":per_hour_rate_cf
				})

		if len(target.get("items")) == 0:
			frappe.throw(_("All items have already been Invoiced/Returned"))

		doc = frappe.get_doc(target)
		doc.bill_no = source.name
		# doc.payment_terms_template = get_payment_terms_template(source.service_by_supplier, "Supplier",get_default_company())
		# doc.run_method("onload")
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