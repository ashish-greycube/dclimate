# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	if not filters : filters = {}
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [{
			"fieldname" : "serial_number",
			"label" : "Serial No",
			"fieldtype" : "Link",
			"options": "Serial No",
			"width" : 150
		},
		{
			"fieldname" : "item_code",
			"label" : "Item Code",
			"fieldtype" : "Link",
			"options": "Item",
			"width" : 120
		},
		{
			"fieldname" : "warranty_expiry_date",
			"label" : "Warranty Expiry Date",
			"fieldtype" : "Date",
			"width" : 140
		},
		{
			"fieldname" : "labor_warranty_expiry_date",
			"label" : "Labor Warranty Expiry Date",
			"fieldtype" : "Date",
			"width" : 140
		},
		{
			"fieldname" : "amc_expiry_date",
			"label" : "AMC Expiry Date",
			"fieldtype" : "Date",
			"width" : 140
		},
		{
			"fieldname" : "installation_note",
			"label" : "Installation Note",
			"fieldtype" : "Link",
			"options": "Installation Note",
			"width" : 150
		},
		{
			"fieldname" : "customer_name",
			"label" : "Customer Name",
			"fieldtype" : "Data",
			"width" : 150
		},
		{
			"fieldname" : "delivery_note",
			"label" : "Delivery Note",
			"fieldtype" : "Data",
			"width" : 150
		},
		{
			"fieldname" : "latest_delivery_note_date",
			"label" : "Latest Delivery Note Date",
			"fieldtype" : "Date",
			"width" : 140
		},
		{
			"fieldname" : "sales_invoice",
			"label" : "Sales Invoice",
			"fieldtype" : "Data",
			"width" : 150
		},
		{
			"fieldname" : "latest_sales_invoice_date",
			"label" : "Latest Sales Invoice Date",
			"fieldtype" : "Date",
			"width" : 140
		},
		{
			"fieldname" : "stock_entry",
			"label" : "Stock Entry",
			"fieldtype" : "Data",
			"width" : 150
		},
		{
			"fieldname" : "latest_stock_entry_date",
			"label" : "Latest Stock Entry Date",
			"fieldtype" : "Date",
			"width" : 140
		}]


def get_data(filters):

	conditions = ""
	
	if filters.get("serial_no"):
		conditions = " AND sn.name = '{0}'".format(filters["serial_no"])
		

	data = frappe.db.sql(
		"""
		SELECT
			sn.name AS "serial_number",
			sn.item_code AS "item_code",
			sn.warranty_expiry_date AS "warranty_expiry_date",    
			sn.labor_warranty_expiry_date_cf as "labor_warranty_expiry_date",
			sn.amc_expiry_date as "amc_expiry_date",
			sn.installation__note_cf AS "installation_note",
			sn.customer AS "customer_name",    
			si.name as sales_invoice,
			si.posting_date as latest_sales_invoice_date,
			dn.name as delivery_note,
			dn.posting_date as latest_delivery_note_date,
			se_bundle.voucher_no as stock_entry,
			se_bundle.posting_date as latest_stock_entry_date
		FROM
			`tabSerial No` sn
			left outer join 
			`tabInstallation Details CT` in_item ON in_item.ac_serial_no=sn.name and in_item.parent LIKE CONCAT('%', 'SINV-', '%')
			left outer JOIN 
			`tabSales Invoice` si on si.name=in_item.parent
			left outer join 
			`tabInstallation Details CT` dn_item ON dn_item.ac_serial_no=sn.name and dn_item.parent LIKE CONCAT('%', 'MAT-DN', '%')
			left outer JOIN 
			`tabDelivery Note` dn on dn.name=dn_item.parent
		LEFT JOIN (
			SELECT 
				sbe.serial_no, sbb.voucher_no AS voucher_no,sbb.posting_date AS posting_date
			FROM `tabSerial and Batch Entry` sbe
			JOIN `tabSerial and Batch Bundle` sbb ON sbe.parent = sbb.name AND sbb.docstatus = 1
			WHERE sbb.voucher_type = 'Stock Entry'
		) se_bundle ON se_bundle.serial_no = sn.name 
		where dn.docstatus != 2 AND si.docstatus != 2  {0}""".format(conditions), as_dict=1, debug=1)
	return data
