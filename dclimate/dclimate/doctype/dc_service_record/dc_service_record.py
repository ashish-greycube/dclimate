# Copyright (c) 2021, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class DCServiceRecord(Document):
	def validate(self):
		total_srt_hours=0
		total_srt_cost=0
		supplier_price_list=self.supplier_price_list
		for job_item in self.job_codes:
			if job_item.job_code:
				job_cost_by_supplier=frappe.db.get_all('Item Price', filters={
    'price_list': ['=', supplier_price_list],
		'item_code': ['=', job_item.job_code],
		'valid_from': ['<=', nowdate()]
})
			if job_cost_by_supplier[0][0]:
				total_srt_cost+=job_item.hours*job_cost_by_supplier[0][0]
			else:
				frappe.throw(msg=_("Item price for job code {0} not found in the supplier price list {1}. Please contact DClimate"
						.format(job_item.job_code,supplier_price_list)),title='Job price not found error.')
			if job_item.hours:
				total_srt_hours=+job_item.hours
		self.total_srt_hours=total_srt_hours
		self.total_srt_cost=total_srt_cost