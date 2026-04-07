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
			"fieldname" : "delivery_note_date",
			"label" : "Delivery Note Date",
			"fieldtype" : "Data",
			"width" : 140
		},
		{
			"fieldname" : "sales_invoice",
			"label" : "Sales Invoice",
			"fieldtype" : "Data",
			"width" : 150
		},
		{
			"fieldname" : "sales_invoice_date",
			"label" : "Sales Invoice Date",
			"fieldtype" : "Data",
			"width" : 140
		},
		{
			"fieldname" : "stock_entry",
			"label" : "Stock Entry",
			"fieldtype" : "Data",
			"width" : 150
		},
		{
			"fieldname" : "stock_entry_date",
			"label" : "Stock Entry Date",
			"fieldtype" : "Data",
			"width" : 140
		}]


def get_data(filters):

	conditions = ""
	
	if filters.get("serial_no"):
		conditions = " WHERE  sn.name = '{0}'".format(filters["serial_no"])
		

	data = frappe.db.sql(
		"""
SELECT
    sn.name AS "serial_number",
    sn.item_code AS "item_code",  
    sn.warranty_expiry_date AS "warranty_expiry_date",    
    sn.labor_warranty_expiry_date_cf AS "labor_warranty_expiry_date",
    sn.amc_expiry_date AS "amc_expiry_date",
    sn.installation__note_cf AS "installation_note",
    sn.customer AS "customer_name",  
    GROUP_CONCAT(DISTINCT CASE WHEN ledger.voucher_type = 'Delivery Note' THEN ledger.voucher_no END SEPARATOR ', ') AS "delivery_note",
    GROUP_CONCAT(DISTINCT CASE WHEN ledger.voucher_type = 'Delivery Note' THEN ledger.posting_date END SEPARATOR ', ') AS "delivery_note_date",
    GROUP_CONCAT(DISTINCT CASE WHEN ledger.voucher_type = 'Sales Invoice' THEN ledger.voucher_no END SEPARATOR ', ') AS "sales_invoice",
    GROUP_CONCAT(DISTINCT CASE WHEN ledger.voucher_type = 'Sales Invoice' THEN ledger.posting_date END SEPARATOR ', ') AS "sales_invoice_date",
    GROUP_CONCAT(DISTINCT CASE WHEN ledger.voucher_type = 'Stock Entry' THEN ledger.voucher_no END SEPARATOR ', ') AS "stock_entry",
    GROUP_CONCAT(DISTINCT CASE WHEN ledger.voucher_type = 'Stock Entry' THEN ledger.posting_date END SEPARATOR ', ') AS "stock_entry_date"
FROM
    `tabSerial No` sn
JOIN (
    SELECT 
        sbe.serial_no AS search_sn, 
        sbb.voucher_type, 
        sbb.voucher_no,
        sbb.posting_date
    FROM `tabSerial and Batch Entry` sbe
    JOIN `tabSerial and Batch Bundle` sbb ON sbe.parent = sbb.name AND sbb.docstatus = 1
    WHERE sbb.voucher_type IN ('Delivery Note', 'Sales Invoice', 'Stock Entry')     
    UNION
    SELECT 
        dni.serial_no AS search_sn, 
        'Delivery Note' AS voucher_type, 
        dni.parent AS voucher_no,
        dn.posting_date
    FROM `tabDelivery Note Item` dni 
    JOIN `tabDelivery Note` dn ON dn.name = dni.parent
    WHERE dni.docstatus = 1 AND dni.serial_no IS NOT NULL AND dni.serial_no != ''
  UNION
    SELECT 
        sii.serial_no AS search_sn, 
        'Sales Invoice' AS voucher_type, 
        sii.parent AS voucher_no,
        si.posting_date
    FROM `tabSales Invoice Item` sii 
    JOIN `tabSales Invoice` si ON si.name = sii.parent
    WHERE sii.docstatus = 1 AND sii.serial_no IS NOT NULL AND sii.serial_no != ''
    UNION
    SELECT 
        sed.serial_no AS search_sn, 
        'Stock Entry' AS voucher_type, 
        sed.parent AS voucher_no,
        se.posting_date
    FROM `tabStock Entry Detail` sed 
    JOIN `tabStock Entry` se ON se.name = sed.parent
    WHERE sed.docstatus = 1 AND sed.serial_no IS NOT NULL AND sed.serial_no != ''
  UNION
    SELECT 
        dn_ct.ac_serial_no AS search_sn, 
        'Delivery Note' AS voucher_type, 
        dn_ct.parent AS voucher_no,
        dn.posting_date
    FROM `tabInstallation Details CT` dn_ct
    JOIN `tabDelivery Note` dn ON dn.name = dn_ct.parent
    WHERE dn_ct.ac_serial_no IS NOT NULL AND dn_ct.ac_serial_no != ''
      AND (dn_ct.parenttype = 'Delivery Note' OR dn_ct.parent LIKE '%MAT-DN%')
     UNION
    SELECT 
        si_ct.ac_serial_no AS search_sn, 
        'Sales Invoice' AS voucher_type, 
        si_ct.parent AS voucher_no,
        si.posting_date
    FROM `tabInstallation Details CT` si_ct
    JOIN `tabSales Invoice` si ON si.name = si_ct.parent
    WHERE si_ct.ac_serial_no IS NOT NULL AND si_ct.ac_serial_no != ''
      AND (si_ct.parenttype = 'Sales Invoice' OR si_ct.parent LIKE '%SINV-%')
) AS ledger 
    ON (ledger.search_sn = sn.name OR ledger.search_sn LIKE CONCAT('%', sn.name, '%'))
	{0}
GROUP BY 
    sn.name, 
    sn.item_code;""".format(conditions), as_dict=1, debug=1)
	return data
