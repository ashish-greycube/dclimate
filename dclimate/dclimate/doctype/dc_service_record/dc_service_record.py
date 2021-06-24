# Copyright (c) 2021, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,get_link_to_form
from frappe import _
from erpnext import get_default_company

class DCServiceRecord(Document):
	def on_submit(self):
		purchase_invoice=make_purchase_invoice(self.name)
		frappe.msgprint(msg=_("Purchase Invoice {0} is created based on DC Service Record {1}"
		.format(frappe.bold(get_link_to_form("Purchase Invoice",purchase_invoice)),frappe.bold(self.name))),
		title="Purchase Invoice is created.",
		indicator="green")

	def validate(self):
		total_srt_hours=0
		total_srt_cost=0
		supplier_price_list=self.supplier_price_list
		if self.job_codes:
			if not supplier_price_list:
				frappe.throw(msg=_('Please define price list for supplier {0}'.format(frappe.bold(get_link_to_form('Supplier',self.service_by_supplier)))),title="Missing supplier price list.")
			for job_item in self.job_codes:
				if job_item.job_code:
					job_cost_by_supplier=frappe.db.get_all('Item Price', filters={
			'price_list': ['=', supplier_price_list],
			'item_code': ['=', job_item.job_code],
			'valid_from': ['<=', nowdate()]
				},
				fields=['price_list_rate'])
				print('-'*100)
				print(job_cost_by_supplier)
				if job_cost_by_supplier and job_cost_by_supplier[0]:
					total_srt_cost=total_srt_cost+job_item.hours*job_cost_by_supplier[0].get('price_list_rate')
				else:
					frappe.throw(msg=_("Item price for job code {0} not found in the supplier price list {1}. Please contact DClimate"
							.format(frappe.bold(job_item.job_code),frappe.bold(supplier_price_list))),title='Job price not found error.')
				if job_item.hours:
					total_srt_hours=total_srt_hours+job_item.hours
			self.total_srt_hours=total_srt_hours
			self.total_srt_cost=total_srt_cost


@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	from erpnext.accounts.party import get_payment_terms_template

	doc = frappe.get_doc('DC Service Record', source_name)
	def set_missing_values(source, target):
		# target.set_posting_time=1
		# target.posting_date=source.completion_date
		if len(target.get("items")) == 0:
			frappe.throw(_("All items have already been Invoiced/Returned"))

		doc = frappe.get_doc(target)
		doc.posting_date=source.completion_date
		doc.ignore_pricing_rule = 1
		doc.bill_no = source.name
		doc.payment_terms_template = get_payment_terms_template(source.service_by_supplier, "Supplier",get_default_company())
		# doc.run_method("onload")
		doc.run_method("set_missing_values")
		doc.run_method("calculate_taxes_and_totals")

	# def update_parts_item(source_doc, target_doc, source_parent):
	# 	if source_parent.parts_warranty_status=='Under Warranty':
	# 		target_doc.item_code =source_doc.item
	# 		target_doc.qty =source_doc.qty

	# def update_job_item(source_doc, target_doc, source_parent):
	# 	if source_parent.labor_warranty_status=='Under Warranty':
	# 		target_doc.item_code =source_doc.job_code
	# 		target_doc.qty =source_doc.hours

	doclist = get_mapped_doc("DC Service Record", source_name,	{
		"DC Service Record": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"service_by_supplier":"supplier",
				"supplier_price_list": "buying_price_list",
  			"received_date": "bill_date" ,
				"technician":"contact_person",
				"completion_date":"posting_date"
			},
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"DC Service Record Parts Detail": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"item": "item_code",
				"qty": "qty",
			},
			# "postprocess": update_parts_item,
		},
		"DC Service Record Job Codes Detail": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"job_code": "item_code",
				"hours": "qty",
			},
			# "postprocess": update_job_item,
		},		
		"Purchase Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges",
			"add_if_empty": True
		}
	}, target_doc, set_missing_values)
	doclist.save(ignore_permissions=True)
	return doclist.name			