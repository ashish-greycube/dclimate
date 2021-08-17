import frappe
from frappe.utils import add_to_date
from frappe import _
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

def onload(self,method):
    if self.name:
        load_installation_note_details_and_remarks(self)

def load_installation_note_details_and_remarks(self):
    if self.docstatus!=2:
        if self.installation_remarks_cf==None and len(self.installation_detail_ct)==0:
            for item in self.items:
                serial_nos=get_serial_nos(item.serial_no)
                for serial_no in serial_nos:
                    serial_no_doc = frappe.get_doc('Serial No', serial_no)
                    if serial_no_doc.installation__note_cf:
                        installation_note = frappe.get_doc('Installation Note', serial_no_doc.installation__note_cf)
                        supplier_name=frappe.db.get_value('Supplier', installation_note.installed_by_supplier_cf, 'supplier_name')

                        self.append("installation_detail_ct", {
                                "ac_serial_no":serial_no,
                                "truck_vin": installation_note.truck_vin_cf or '',
                                "truck_number":installation_note.truck_number_cf or '',
                                "installed_by":supplier_name or '',
                                "installation_date":installation_note.inst_date or '',
                                "remarks":installation_note.remarks or ''
                            })  
                        frappe.msgprint(msg=_("Installation details are updated."), indicator='green',alert=True)
                        self.save(ignore_permissions=True)
                        frappe.db.commit()

                        if self.installation_remarks_cf==None :
                            city=frappe.db.get_value('Address', installation_note.supplier_location_cf, 'city')
                            state=frappe.db.get_value('Address', installation_note.supplier_location_cf, 'state')
                            self.installation_remarks_cf="Installed at {0}, {1} {2}".format(supplier_name or '',city or '',state or '')       
                            frappe.msgprint(msg=_("Installation remarks are updated."), indicator='green',alert=True)
                            self.save(ignore_permissions=True)
                            frappe.db.commit()
        else:
            frappe.msgprint(msg=_("Existing installation notes found and hence no update."), indicator='orage', alert=True)
def on_submit_of_delivery_note(self,method):
  check_serial_no_is_associated_with_installation_note(self,method)
  update_warranty_info_based_on_delivery_note(self,method)

def check_serial_no_is_associated_with_installation_note(self,method):
    for item in self.items:
      serial_nos=get_serial_nos(item.serial_no)
      for serial_no in serial_nos:
        serial_no_doc = frappe.get_doc('Serial No', serial_no)
        if not serial_no_doc.installation__note_cf:
          frappe.throw(msg=_("Serial no. {0} for item {1} is not associated with any installation note.<br>Please correct it to continue..".format(serial_no,item.item_code) ),title='Serial No. not associated with Installation Note')
        elif serial_no_doc.installation__note_cf:
            installation_note_customer=frappe.db.get_value('Installation Note', serial_no_doc.installation__note_cf, 'customer')
            if self.customer != installation_note_customer:
                frappe.throw(msg=_("Serial no. {0} installed on different customer.<br>Please correct it to continue..".format(serial_no) ),title='Serial No. is used by different customer.')

def update_warranty_info_based_on_delivery_note(self,method):
    if method=='on_submit' and self.is_return==0:
        dc_warranty_items=get_warranty_type_item(self)
        if dc_warranty_items:
            # multiple warranty type items found..so return
            if len(dc_warranty_items)>1:
                frappe.throw(msg=_('{0} items of type warranty found. You can have only one wrranty type item per delivery note.' \
                    .format( frappe.bold(' '.join(str(e))for e in dc_warranty_items))),title='Multiple Warranty type items.')                
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
        dc_warranty_items=get_warranty_type_item(self)
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
        if frappe.db.exists({
            "doctype":'DC Warranty Type',
            'warranty_item':item.item_code
        }):
            
            dc_warranty_items.append(item.item_code)
    return dc_warranty_items            


def remove_warranty_details_from_serial_no(serial_no):
    serial_no=frappe.get_doc('Serial No',serial_no)
    serial_no.parts_warranty_expiry_date_cf=None
    serial_no.labor_warranty_expiry_date_cf=None
    serial_no.total_heater_hours_cf=None
    serial_no.save(ignore_permissions=True)

def update_warranty_details_in_serial_no(posting_date,serial_no,warranty_type):
    dc_warranty_name=frappe.db.get_list('DC Warranty Type', filters=[['warranty_item', '=', warranty_type]],fields=['name'])[0]
    serial_no=frappe.get_doc('Serial No',serial_no)
    warranty_type=frappe.get_doc('DC Warranty Type',dc_warranty_name)
    if warranty_type.parts_warranty_years>0:
        if serial_no.parts_warranty_expiry_date_cf:
            frappe.throw(msg=_('{0} serial no couldnot be updated, as it has existing value {1} for parts warranty expiry date' \
                .format(serial_no.name,serial_no.parts_warranty_expiry_date_cf)),title='Existing value error')
        else:
            serial_no.parts_warranty_expiry_date_cf=add_to_date(posting_date,years=warranty_type.parts_warranty_years)

    if warranty_type.labor_warranty_years>0:
        if serial_no.labor_warranty_expiry_date_cf:
            frappe.throw(msg=_('{0} serial no couldnot be updated, as it has existing value {1} for labor warranty expiry date' \
                .format(serial_no.name,serial_no.labor_warranty_expiry_date_cf)),title='Existing value error')
        else:
            serial_no.labor_warranty_expiry_date_cf=add_to_date(posting_date,years=warranty_type.labor_warranty_years)            

    if warranty_type.total_hours>0:
        if serial_no.total_heater_hours_cf!=0:
            frappe.throw(msg=_('{0} serial no couldnot be updated, as it has existing value {1} for total heater hours' \
                .format(serial_no.name,serial_no.total_heater_hours_cf)),title='Existing value error')
        else:
            serial_no.total_heater_hours_cf=warranty_type.total_hours
    serial_no.save(ignore_permissions=True)

