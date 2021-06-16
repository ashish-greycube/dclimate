import frappe
from frappe import _
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

def update_heater_info_based_on_installation_note(self,method):
  if method=='Submit':
    if self.heater_serial_no_cf and len(self.items)==1:
      serial_nos=get_serial_nos(self.items[0].serial_no)
      if len(serial_nos)==0:
        frappe.msgprint(_("'Items' row doesnot have any serial no.<br> \
                          Hence no update is made to serial no doctype"),alert=True)        
      for serial_no in serial_nos:      
        update_heater_info_in_serial_no(serial_no,self.name,self.heater_serial_no_cf)
        frappe.msgprint(_("'Heater serial #' and 'Installation Note' reference are updated in {0} serial no doctype.".format(frappe.bold(serial_no))),alert=True)
    else:
      frappe.msgprint(_("'Heater Serial No' field is empty OR 'Items' table has more than 1 record.<br> \
                          Hence no update is made to serial no doctype"),alert=True)

  elif method == 'Cancel':
    if len(self.items)==1:
      serial_nos=get_serial_nos(self.items[0].serial_no)
      for serial_no in serial_nos:      
        remove_heater_info_in_serial_no(serial_no,self.name,self.heater_serial_no_cf)
        frappe.msgprint(_("'Heater serial #' and 'Installation Note' reference are removed from {0} serial no doctype.".format(frappe.bold(serial_no))),alert=True)   

def update_heater_info_in_serial_no(serial_no,installation_note_name,heater_serial_no_cf):
  serial_no=frappe.get_doc('Serial No',serial_no)
  if serial_no.heater_serial_no_cf!=None or serial_no.installation_note_cf!=None:
      frappe.throw(_("{0} serial no couldnot be updated, as it has existing value {1} for 'Heater Serial #' \
           or {2} for 'Installation Note' field "
          .format(serial_no.name,serial_no.heater_serial_no_cf,serial_no.installation_note_cf),title='Existing value error'))
  else:
      serial_no.heater_serial_no_cf=heater_serial_no_cf 
      serial_no.installation_note_cf=installation_note_name
      serial_no.save(ignore_permissions=True)

def remove_heater_info_in_serial_no(serial_no):
    serial_no=frappe.get_doc('Serial No',serial_no)
    serial_no.heater_serial_no_cf=None
    serial_no.installation_note_cf=None
    serial_no.save(ignore_permissions=True)  