import frappe
from frappe.utils import add_to_date

def update_warranty_info_in_serial_no(self,method):
    if method=='on_submit':
        pass





def update_warranty_details_in_serial_no(delivery_date,serial_no,warranty_type):
    serial_no=frappe.get_doc('Serial No',serial_no)
    warranty_type=frappe.get_doc('DC Warranty Type',warranty_type)


    if warranty_type.parts_warranty_years>0:
        if serial_no.parts_warranty_expiry_date_cf!=None:
            frappe.throw(_('{0} serial no couldnot be updated, as it has existing value {1} for parts warranty expiry date' \
                .format(serial_no.name,serial_no.parts_warranty_expiry_date_cf),title='Existing value error'))
        else:
            serial_no.parts_warranty_expiry_date_cf=add_to_date(delivery_date,years=warranty_type.parts_warranty_years)

    if warranty_type.labor_warranty_years>0:
        if serial_no.labor_warranty_expiry_date_cf!=None:
            frappe.throw(_('{0} serial no couldnot be updated, as it has existing value {1} for labor warranty expiry date' \
                .format(serial_no.name,serial_no.labor_warranty_expiry_date_cf),title='Existing value error'))
        else:
            serial_no.labor_warranty_expiry_date_cf=add_to_date(delivery_date,years=warranty_type.labor_warranty_years)            


    if warranty_type.total_hours>0:
        if serial_no.total_heater_hours_cf!=0:
            frappe.throw(_('{0} serial no couldnot be updated, as it has existing value {1} for total heater hours' \
                .format(serial_no.name,serial_no.total_heater_hours_cf),title='Existing value error'))
        else:
            serial_no.total_heater_hours_cf=warranty_type.total_hours
        
    serial_no.save(ignore_permissions=True)

