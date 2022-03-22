// Copyright (c) 2021, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('DClimate Settings', {
	refresh: function(frm) {
		frm.set_query('after_sales_income_account',()=>{
			return {
				filters:{
					"account_type": ["=",["Income Account"]],
				}
			}
		})
	}
});
