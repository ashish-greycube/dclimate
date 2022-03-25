
import frappe
from frappe import _


def set_income_account_for_dc_out_of_warranty_service_record(self,method):
    if self.dc_service_out_of_warranty_cf:
        after_sales_income_account = frappe.db.get_single_value('DClimate Settings', 'after_sales_income_account')
        if after_sales_income_account:
            for item in self.items:
                item.income_account=after_sales_income_account
            frappe.msgprint(msg=_("Income Account {0} is set in Sales Invoice Items".format(frappe.bold(after_sales_income_account))),title="Delivery Note is created.",indicator="green",alert=1)            