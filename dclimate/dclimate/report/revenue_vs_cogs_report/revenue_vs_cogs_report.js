// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.require("assets/erpnext/js/financial_statements.js", function () {
	frappe.query_reports["Revenue vs COGS Report"] = $.extend({},
		erpnext.financial_statements);

	frappe.query_reports["Revenue vs COGS Report"]["filters"].push(
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "income_account",
			"label": __("Income Account"),
			"fieldtype": "Link",
			"options": "Account"
		},
		{
			"fieldname": "expense_account",
			"label": __("Expense Account"),
			"fieldtype": "Link",
			"options": "Account"
		}
	);
});
