// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["DClimate Item Shortage Report"] = {
	"filters": [

		
		{
            "fieldname":"item_group",
            "label": 'Item Group',
            "fieldtype": "Link",
            "options": "Item Group",
			   
		},
		{
            "fieldname":"item_code",
            "label": 'Item Code',
            "fieldtype": "Link",
            "options": "Item",
			   
		},
		{
            "fieldname":"warehouse",
            "label": 'Warehouse',
            "fieldtype": "Link",
		"options": "Warehouse",
			
			   
		},
		{
            "fieldname":"type",
            "label": 'Type',
            "fieldtype": "Select",
            "options": ["All","Only Shortage"],
			   
		},
            

	]
};
