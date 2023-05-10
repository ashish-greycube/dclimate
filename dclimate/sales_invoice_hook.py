
import frappe
from frappe import _
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

def set_income_account_for_dc_out_of_warranty_service_record(self,method):
    if self.dc_service_out_of_warranty_cf:
        after_sales_income_account = frappe.db.get_single_value('DClimate Settings', 'after_sales_income_account')
        if after_sales_income_account:
            for item in self.items:
                item.income_account=after_sales_income_account
            frappe.msgprint(msg=_("Income Account {0} is set in Sales Invoice Items".format(frappe.bold(after_sales_income_account))),title="Delivery Note is created.",indicator="green",alert=1)            

def synch_serial_no_in_items_and_installation_detail_tables(self,method):
    to_remove = []
    si_item_serial_nos=[]
    for item in self.get('items'):
        if item.delivery_note:
            si_serial_nos = get_serial_nos(item.serial_no)
            si_item_serial_nos.extend(si_serial_nos)
    
    si_item_serial_nos=list(set(si_item_serial_nos))

    if len(si_item_serial_nos)>0:
        for installation_row in self.get('installation_detail_ct'):
            if installation_row.ac_serial_no in si_item_serial_nos:   
                pass
            else:    
                to_remove.append(installation_row)
                frappe.msgprint(msg=_("Row {0} : with serial no {1}  is removed".format(installation_row.idx,frappe.bold(installation_row.ac_serial_no))),
                               title="Installation Details is updated.",indicator="orange",alert=1)

    if len(to_remove)>0:
        [self.installation_detail_ct.remove(d) for d in to_remove]

        for index,installation_row in enumerate(self.get('installation_detail_ct')):
            installation_row.idx = index+1

    if len(to_remove)==0 and self.get('installation_detail_ct') and len(self.get('installation_detail_ct'))>0:
        self.installation_detail_ct = []
        frappe.msgprint(msg=_("A/C Serial no are not present in Items table. Hence Installation Details is made empty"),
                            title="Installation Details is made empty.",indicator="red",alert=1)

