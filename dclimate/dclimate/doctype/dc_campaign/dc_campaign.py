# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate,get_link_to_form,get_datetime,getdate,get_time,today
from frappe import _
from frappe.contacts.doctype.address.address import get_address_display

class DCCampaign(Document):
	@frappe.whitelist()
	def sync_dc_campaign_completion_form(self):
		for serial_detail in self.dc_campaign_serial_no:
			if serial_detail.dc_campaign_completion_form:
				serial_detail.status=frappe.db.get_value('DC Campaign Completion Form', serial_detail.dc_campaign_completion_form, 'status')
				serial_detail.purchase_invoice=frappe.db.get_value('DC Campaign Completion Form', serial_detail.dc_campaign_completion_form, 'purchase_invoice')
				serial_detail.completion_date=getdate(frappe.db.get_value('DC Campaign Completion Form', serial_detail.dc_campaign_completion_form, 'completion_date_time'))
				serial_detail.stock_entry=frappe.db.get_value('DC Campaign Completion Form', serial_detail.dc_campaign_completion_form, 'material_issue')
			if serial_detail.serial_no and not serial_detail.dc_campaign_completion_form:
				completion_form, status=self.create_dc_campaign_completion_form(serial_no=serial_detail.serial_no)
				if completion_form!=0:
					serial_detail.dc_campaign_completion_form=completion_form	
					serial_detail.status=status	

	def create_dc_campaign_completion_form(self,serial_no):
		installation__note_cf=frappe.db.get_value("Serial No", serial_no, 'installation__note_cf')
		installation__note=frappe.db.get_value('Installation Note', installation__note_cf, ['truck_vin_cf','truck_number_cf','customer'], as_dict=1)
		completion_form = frappe.new_doc("DC Campaign Completion Form")
		completion_form.dc_campaign=self.name
		completion_form.serial_no=serial_no
		completion_form.item_name=frappe.db.get_value("Serial No", serial_no, 'item_name')
		completion_form.end_customer=frappe.db.get_value("Serial No", serial_no, 'end_customer_cf')
		completion_form.end_customer_name=frappe.db.get_value("Customer",completion_form.end_customer, 'customer_name')
		completion_form.parts_warranty_expiry_date=frappe.db.get_value("Serial No", serial_no, 'parts_warranty_expiry_date_cf')
		if completion_form.parts_warranty_expiry_date:
			completion_form.parts_warranty_status='Under Warranty' if (getdate(completion_form.parts_warranty_expiry_date) >=getdate()) else 'Warranty Expired'
		completion_form.heater_hours=frappe.db.get_value("Serial No", serial_no, 'total_heater_hours_cf')
		completion_form.labor_warranty_expiry_date=frappe.db.get_value("Serial No", serial_no, 'labor_warranty_expiry_date_cf')
		if completion_form.labor_warranty_expiry_date:
			completion_form.labor_warranty_status='Under Warranty' if (getdate(completion_form.labor_warranty_expiry_date) >=getdate()) else 'Warranty Expired'
		completion_form.service_by_supplier=self.supplier
		supplier_address=frappe.db.get_list('Dynamic Link',  fields=['parent'],filters={'link_doctype': 'Supplier','parentfield' : 'links','parenttype' :'Address','link_name':completion_form.service_by_supplier})
		if len(supplier_address)>0:
			completion_form.supplier_address=supplier_address[0].parent
			completion_form.supplier_address_display=get_address_display(completion_form.supplier_address)
		completion_form.status='Open'
		completion_form.issue_description=self.description
		completion_form.default_parts_issue_warehouse=self.default_parts_issue_warehouse
		if installation__note and len(installation__note)>0:
			completion_form.truck_vin=installation__note.truck_vin_cf
			completion_form.truck_number=installation__note.truck_number_cf
		completion_form.customer=installation__note.customer or frappe.db.get_value("Serial No", serial_no, 'customer')
		for parts in self.parts_detail:
			cf_parts_child = completion_form.append("parts_detail")
			cf_parts_child.item = parts.item		
			cf_parts_child.qty = parts.qty
		for job in self.job_codes:
			cf_jobs_child = completion_form.append("job_codes")
			cf_jobs_child.job_code=job.job_code
			cf_jobs_child.hours=job.hours
		completion_form.total_srt_hours=self.total_srt_hours
		completion_form.total_srt_cost=self.total_srt_cost
		completion_form.run_method('set_missing_values')
		completion_form.save(ignore_permissions=True)
		return completion_form.name,completion_form.status

	def validate(self):
		self.calculate_total_srt_values()

	def calculate_total_srt_values(self):
		# validate job price is present in supplier price list and calculate total hours and cost
		total_srt_hours=0
		total_srt_cost=0
		# supplier_price_list=self.supplier_price_list
		per_hour_rate_cf = frappe.db.get_value('Supplier', self.supplier, 'per_hour_rate_cf')
		if not per_hour_rate_cf:
			frappe.throw(msg=_('Per hour job rate is not defined for supplier {0}. Please contact DClimate'.format(frappe.bold(get_link_to_form('Supplier',self.supplier)))),title="Missing per hour job rate for supplier.")
		if self.job_codes:
			for job_item in self.job_codes:
				if job_item.job_code:
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
