# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = [
			{
				"label": "Item Code",
				"fieldname":"item_code",
				"fieldtype": "Link",
				"options":"Item",
				"width":300
			},
			{
				"label": 'Item Name',
				"fieldname":"item_name",
				"fieldtype": "Data",
				"width":0,
				"hidden":1

			},
			{
				"label": 'Item Group',
				"fieldname":"item_group",
				"fieldtype": "Link",	
				"options":"Item Group",
				"width":180			
			},
			{
				"label": 'Warehouse',
				"fieldname":"warehouse",
				"fieldtype": "Link",
				"options":"Warehouse",
				"width":200
			},	
			{
				"label": 'Actual Qty',
				"fieldname":"actual_qty",
				"fieldtype": "Float",	
				"width":120
			},					
			{
				"label": 'Safety Stock',
				"fieldname":"safety_stock",
				"fieldtype": "Float",
				"width":120	
			},
			{
				"label": 'Buffer Stock',
				"fieldname":"buffer_stock",
				"fieldtype": "Float",	
				"width":120
			},			
			{
				"label": 'Shortage Qty Ref',
				"fieldname":"shortage_qty_reference",
				"fieldtype": "Float",
				"width":140	
			},
		]
	
	data =[]
	query_filters = {}
	query_filters_warehouse ={}

	fields_item = ["item_code","item_name","item_group",	"safety_stock",	]
	fields_warehouse = ["item_code","warehouse","actual_qty"]

	for field in ["item_code", "item_group"]:
		if filters.get(field):
			query_filters[field] = ("in", filters.get(field))

	for field in ["item_code","warehouse"]:
		if filters.get(field):
			query_filters_warehouse[field] = ("in", filters.get(field))

	items = frappe.get_all("Item", fields=fields_item, filters=query_filters)
	bins = frappe.get_all("Bin", fields=fields_warehouse, filters=query_filters_warehouse)

	for bin in bins:
		for item in items:
			if bin.item_code == item.item_code:	
				buffer_stock = flt(bin.actual_qty) - flt(item.safety_stock)
				baq = flt(bin.actual_qty)
				iss = flt(item.safety_stock)
				if(iss > 0):
					shortage_qty_reference = baq / iss
				else:
					shortage_qty_reference = 0

				if(filters.get("type") == 'Only Shortage'):
					if(buffer_stock <= 0):
						data.append([
						item.item_code,
						item.item_name,
						item.item_group,
						bin.warehouse,
						flt(bin.actual_qty,1),
						flt(item.safety_stock,1),
						flt(buffer_stock,1),
						flt(shortage_qty_reference,1)	
				])
				else:
					data.append([
						item.item_code,
						item.item_name,
						item.item_group,
						bin.warehouse,
						flt(bin.actual_qty,1),
						flt(item.safety_stock,1),
						flt(buffer_stock,1),
						flt(shortage_qty_reference,1)		
				])
	# sort by shortage_qty_reference desc and item_code
	data = sorted(data, key = lambda x: (x[7], x[0]))			
	return columns, data