// Copyright (c) 2023, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["DClimate Item Shortage Report"] = {
      "filters": [
            {
                  "fieldname": "warehouse",
                  "label": 'Warehouse',
                  "fieldtype": "Link",
                  "options": "Warehouse",
            },            
            {
                  "fieldname": "item_group",
                  "label": 'Item Group',
                  "fieldtype": "Link",
                  "options": "Item Group",
            },
            {
                  "fieldname": "item_code",
                  "label": 'Item Code',
                  "fieldtype": "Link",
                  "options": "Item",
            },
            {
                  "fieldname": "type",
                  "label": 'Type',
                  "fieldtype": "Select",
                  "options": ["All", "Only Shortage"],
                  "default": "All",
            }
      ],
      formatter: function (value, row, column, data, default_formatter) {
            value = default_formatter(value, row, column, data);
            let type = frappe.query_report.get_filter_value('type')
            if (type == 'All') {
                  if (data.buffer_stock <= 0) {
                        value = '<b style="color:red">' + value + '</b>';
                  }
            }
            // for other normal 
            return value;
      },
};