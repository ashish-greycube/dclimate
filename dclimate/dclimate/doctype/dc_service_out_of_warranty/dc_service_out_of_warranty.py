# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

from distutils.log import debug
import frappe
import erpnext
from frappe.model.document import Document
from frappe.utils import today
from frappe.utils import nowdate,get_link_to_form,get_datetime,getdate,get_time
from frappe import _
from erpnext.stock.get_item_details import get_item_details
from frappe.model.mapper import get_mapped_doc



class DCServiceOutofWarranty(Document):
	def on_submit(self):
		if not self.completion_date_time:
			frappe.throw(msg=_("Please enter <b>Completion Date Time</b> value"),title="Missing Completion Date Time.")	

		if not self.end_customer:
			frappe.throw(msg=_("Please enter <b>End Customer</b> value in serial no"),title="Missing End Customer.")	

		delivery_note=make_delivery_note(self.name)		
		if delivery_note!=0:
			frappe.msgprint(msg=_("Delivery Note {0} is created based on DC Service Out of Warranty {1}"
			.format(frappe.bold(get_link_to_form("Delivery Note",delivery_note)),frappe.bold(self.name))),
			title="Delivery Note is created.",
			indicator="green")

	def validate(self):
		price_list = (frappe.db.get_single_value('Selling Settings', 'selling_price_list') or frappe.db.get_value('Price List', _('Standard Selling')))		
		customer_default_price_list=frappe.db.get_value('Customer', self.end_customer, 'default_price_list')
		
		# calculate total hours and cost for job 
		total_srt_hours=0
		total_srt_cost=0

		if self.job_codes:
			for job_item in self.job_codes:

				if job_item.job_code:
					customer_default_price_list_rate=frappe.db.get_all('Item Price', filters={
																					'price_list': ['=', customer_default_price_list ],
																					'item_code': ['=', job_item.job_code]
																					}, fields='price_list_rate')	
					price_list_rate =frappe.db.get_all('Item Price', filters={
																					'price_list': ['=',  price_list],
																					'item_code': ['=', job_item.job_code]
					
																					}, fields='price_list_rate')
					if len(customer_default_price_list_rate)>0:
						per_hour_rate_cf=customer_default_price_list_rate[0].price_list_rate
					elif len(price_list_rate)>0:
						per_hour_rate_cf=price_list_rate[0].price_list_rate
					else:
						per_hour_rate_cf=0
					total_srt_cost=total_srt_cost+job_item.hours*per_hour_rate_cf
				if job_item.hours:
					total_srt_hours=total_srt_hours+job_item.hours
			self.total_srt_hours=total_srt_hours
			self.total_srt_cost=total_srt_cost

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def fetch_serial_no(doctype, txt, searchfield, start, page_len, filters):
	data = frappe.db.sql(""" SELECT name,serial_no,item_code FROM `tabSerial No`
WHERE installation__note_cf IS NOT NULL 
and parts_warranty_expiry_date_cf < %s 
and labor_warranty_expiry_date_cf < %s""", (today(), today()))
	return data

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
	after_sales_income_account = frappe.db.get_single_value('DClimate Settings', 'after_sales_income_account')
	price_list = (frappe.db.get_single_value('Selling Settings', 'selling_price_list') or frappe.db.get_value('Price List', _('Standard Selling')))		

	def set_missing_values(source, target):
		customer_default_price_list=frappe.db.get_value('Customer', source.end_customer, 'default_price_list')
		target.customer=source.end_customer
		target.dc_service_out_of_warranty_cf=source.name
		target.set_posting_time=1
		target.posting_date=getdate(source.completion_date_time)
		target.posting_time=get_time(source.completion_date_time)
		target.selling_price_list=customer_default_price_list or price_list

		for item in source.parts_detail:

			target.append('items',{
			"item_code":item.item,
			"qty" :item.qty,
			})

		for item in source.job_codes:

			target.append('items',{
			"item_code":item.job_code,
			"qty" :item.hours,
			})

		if len(target.get("items")) == 0:
			frappe.throw(_("There are no items to make Delivery Note"))

		# target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	doclist = get_mapped_doc("DC Service Out of Warranty", source_name, 	{
		"DC Service Out of Warranty": {
			"doctype": "Delivery Note",
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc, set_missing_values,ignore_permissions=True)
	doclist.save(ignore_permissions=True)
	return doclist.name		