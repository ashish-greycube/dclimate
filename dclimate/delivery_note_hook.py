import frappe
from frappe.utils import add_to_date
from frappe import _
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

def update_warranty_info_based_on_delivery_note(self,method):
    if method=='on_submit' and self.is_return==0:
        dc_warranty_items=self.get_warranty_type_item()
        if dc_warranty_items:
            # multiple warranty type items found..so return
            if len(dc_warranty_items)>1:
                frappe.throw(_('{0} items of type warranty found. You can have only one wrranty type item per delivery note.' \
                    .format( frappe.bold(' '.join(str(e))for e in dc_warranty_items)),title='Multiple Warranty type items.'))                
            # single warranty type item found...so process it
            elif len(dc_warranty_items)==1:
                dc_warranty_item=dc_warranty_items[0]
                for item in self.items:
                    if item.item_code != dc_warranty_item:
                        serial_nos=get_serial_nos(item.serial_no)
                        for serial_no in serial_nos:
                            update_warranty_details_in_serial_no(self.posting_date,serial_no,dc_warranty_item)
                            frappe.msgprint(_("Warranty details are updated in {0} serial no doctype.".format(frappe.bold(serial_no))),alert=True)
        # there is no dc_warranty_items so nothing to do
        else:
            return
    elif (method=='on_submit' and self.is_return==1) or (method=='on_cancel'):
        dc_warranty_items=self.get_warranty_type_item()
        if len(dc_warranty_items)==1:
            dc_warranty_item=dc_warranty_items[0]
            for item in self.items:
                if item.item_code != dc_warranty_item:
                    serial_nos=get_serial_nos(item.serial_no)
                    for serial_no in serial_nos:
                        remove_warranty_details_from_serial_no(serial_no)
                        frappe.msgprint(_("Warranty details are removed from {0} serial no doctype.".format(frappe.bold(serial_no))),alert=True)            

def get_warranty_type_item(self):
    dc_warranty_items=[]
    for item in self.items:
        if frappe.db.exists('DC Warranty Type',item.item_code):
            dc_warranty_items.append(item.item_code)
    return dc_warranty_items            


def remove_warranty_details_from_serial_no(serial_no):
    serial_no=frappe.get_doc('Serial No',serial_no)
    serial_no.parts_warranty_expiry_date_cf=None
    serial_no.labor_warranty_expiry_date_cf=None
    serial_no.total_heater_hours_cf=None
    serial_no.save(ignore_permissions=True)

def update_warranty_details_in_serial_no(posting_date,serial_no,warranty_type):
    serial_no=frappe.get_doc('Serial No',serial_no)
    warranty_type=frappe.get_doc('DC Warranty Type',warranty_type)

    if warranty_type.parts_warranty_years>0:
        if serial_no.parts_warranty_expiry_date_cf!=None:
            frappe.throw(_('{0} serial no couldnot be updated, as it has existing value {1} for parts warranty expiry date' \
                .format(serial_no.name,serial_no.parts_warranty_expiry_date_cf),title='Existing value error'))
        else:
            serial_no.parts_warranty_expiry_date_cf=add_to_date(posting_date,years=warranty_type.parts_warranty_years)

    if warranty_type.labor_warranty_years>0:
        if serial_no.labor_warranty_expiry_date_cf!=None:
            frappe.throw(_('{0} serial no couldnot be updated, as it has existing value {1} for labor warranty expiry date' \
                .format(serial_no.name,serial_no.labor_warranty_expiry_date_cf),title='Existing value error'))
        else:
            serial_no.labor_warranty_expiry_date_cf=add_to_date(posting_date,years=warranty_type.labor_warranty_years)            

    if warranty_type.total_hours>0:
        if serial_no.total_heater_hours_cf!=0:
            frappe.throw(_('{0} serial no couldnot be updated, as it has existing value {1} for total heater hours' \
                .format(serial_no.name,serial_no.total_heater_hours_cf),title='Existing value error'))
        else:
            serial_no.total_heater_hours_cf=warranty_type.total_hours
        
    serial_no.save(ignore_permissions=True)

