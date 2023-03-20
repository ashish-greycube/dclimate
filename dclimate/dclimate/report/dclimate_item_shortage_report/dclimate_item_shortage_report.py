# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _



def execute(filters=None):
# def execute(filters):
	columns = [
			
			{
				"label": "Item Code",
				"fieldname":"item_code",
				"fieldtype": "link",
				"options":"Item"
			},
			{
				"label": 'Item Name',
				"fieldname":"item_name",
				"fieldtype": "Data"

			},
			{
				"label": 'Item Group',
				"fieldname":"item_group",
				"fieldtype": "link",	
				"options":"Item Group"				
			},
			
			{
				"label": 'Safety Stock',
				"fieldname":"safety_stock",
				"fieldtype": "Data",	
			},
			{
				"label": 'Warehouse',
				"fieldname":"warehouse",
				"fieldtype": "link",
				"options":"Warehouse"
			},
			{
				"label": 'Actual Qty',
				"fieldname":"actual_qty",
				"fieldtype": "Data",	
			},
			{
				"label": 'Buffer Stock',
				"fieldname":"buffer_stock",
				"fieldtype": "Data",	
			},
			{
				"label": 'Shortage Qty Reference',
				"fieldname":"shortage_qty_reference",
				"fieldtype": "Data",	
			},
		]
	
	data =[]
	query_filters = {}
	query_filters_warehouse ={}

	fields = [
		"item_code",
		"item_name",
		"item_group",
		"safety_stock",	
	]
	fields_warehouse = [
		"item_code",
		"warehouse",
		"actual_qty"	
	]
	print('-'*10)
	print('filters',filters)
	
	print('Type filter',filters.get("type"))


	for field in ["item_code", "item_group"]:
		if filters.get(field):
			query_filters[field] = ("in", filters.get(field))

	print('query_filters',query_filters)

	for field in ["item_code","warehouse"]:
		if filters.get(field):
			query_filters_warehouse[field] = ("in", filters.get(field))
	print('query_filters_warehouse',query_filters_warehouse)


	items = frappe.get_all("Item", fields=fields, filters=query_filters)
	bins = frappe.get_all("Bin", fields=fields_warehouse, filters=query_filters_warehouse)
	# print('items',items)
	# print('bins',bins)
	print('-'*10)


	for bin in bins:
		for item in items:
			if bin.item_code == item.item_code:	

				buffer_stock = bin.actual_qty - item.safety_stock

				baq = float(bin.actual_qty)
				iss = item.safety_stock


				if(iss > 0):
					shortage_qty_reference = baq / iss
				else:
					shortage_qty_reference = 0


				print('***',filters.get("type") == 'Only Shortage',buffer_stock)

				if(filters.get("type") == 'Only Shortage'):
					if(buffer_stock <= 0):
						data.append([
						item.item_code,
						item.item_name,
						item.item_group,
						item.safety_stock,
						bin.warehouse,
						bin.actual_qty,
						buffer_stock,
						shortage_qty_reference	
				])
				else:
					data.append([
					item.item_code,
					item.item_name,
					item.item_group,
					item.safety_stock,
					bin.warehouse,
					bin.actual_qty,
					buffer_stock,
					shortage_qty_reference	
				])

				# 	for item in items:
				# 		if(buffer_stock == 0)
	return columns, data