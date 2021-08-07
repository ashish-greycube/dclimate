import frappe
from frappe import _
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
import json


def check_for_single_serial_no(self,method):
    if self.heater_serial_no_cf and len(self.items)==1:
      serial_nos=get_serial_nos(self.items[0].serial_no)
      if len(serial_nos)>1:
        frappe.throw(msg=_("More than one serial no. found in items table.<br> A single serial no is allowed. Please correct it to continue.." ),title='Serial No. Issue')    

def update_heater_info_based_on_installation_note(self,method):
  if method=='on_submit':
    if self.heater_serial_no_cf and len(self.items)==1:
      serial_nos=get_serial_nos(self.items[0].serial_no)
      if len(serial_nos)==0:
        frappe.msgprint(_("'Items' row doesnot have any serial no.<br> \
                          Hence no update is made to serial no doctype"),alert=True)  
      elif len(serial_nos)>1:
        frappe.throw(msg=_("More than one serial no found in items table.<br> A single serial no is allowed." ),title='Serial No. Issue')        
      for serial_no in serial_nos:      
        update_heater_info_in_serial_no(serial_no,self.name,self.heater_serial_no_cf)
        frappe.msgprint(_("'Heater serial #' and 'Installation Note' reference are updated in {0} serial no doctype.".format(frappe.bold(serial_no))),alert=True)
    else:
      frappe.msgprint(_("'Heater Serial No' field is empty OR 'Items' table has more than 1 record.<br> \
                          Hence no update is made to serial no doctype"),alert=True)
  elif method == 'on_cancel':
    if len(self.items)==1:
      serial_nos=get_serial_nos(self.items[0].serial_no)
      for serial_no in serial_nos:      
        remove_heater_info_in_serial_no(serial_no)
        frappe.msgprint(_("'Heater serial #' and 'Installation Note' reference are removed from {0} serial no doctype.".format(frappe.bold(serial_no))),alert=True)   

def update_heater_info_in_serial_no(serial_no,installation_note_name,heater_serial_no_cf):
  serial_no=frappe.get_doc('Serial No',serial_no)
  if serial_no.heater_serial_no_cf or serial_no.installation__note_cf:
      frappe.throw(msg=_("{0} serial no couldnot be updated, as it has existing value {1} for 'Heater Serial #' \
           or {2} for 'Installation Note' field "
          .format(serial_no.name,serial_no.heater_serial_no_cf,serial_no.installation__note_cf)),title='Existing value error')
  else:
      serial_no.heater_serial_no_cf=heater_serial_no_cf 
      serial_no.installation__note_cf=installation_note_name
      serial_no.save(ignore_permissions=True)

def remove_heater_info_in_serial_no(serial_no):
    serial_no=frappe.get_doc('Serial No',serial_no)
    serial_no.heater_serial_no_cf=None
    serial_no.installation__note_cf=None
    serial_no.save(ignore_permissions=True)  

@frappe.whitelist()
def get_dc_installation_checklist(checklist_names=None,items=None):
  if checklist_names:
    checklist_names=json.loads(checklist_names)
  
  if items:
    items=json.loads(items)


  print('-'*10,checklist_names,items)
  message=''
  if items and not checklist_names:
    
    for item in items:

      item=frappe.get_doc('Item', item.get('item_code'))

      if item:
        dc_installation_checklist_multi_cf=[]
        data=[]
        for default_installation_checklist in item.default_installation_checklist_multi_cf:
          dc_installation_checklist_multi_cf.append({'dc_installation_checklist':default_installation_checklist.dc_installation_checklist})
          checklist_details=get_checklist_detail(default_installation_checklist.dc_installation_checklist)
          for checklist_detail in checklist_details:
            data.append(checklist_detail)
        message={
          'dc_installation_checklist_multi_cf':dc_installation_checklist_multi_cf,
          'data': data
          }
        return message
  elif checklist_names:
      
      print('checklist_names',checklist_names)
      data=[]
      for checklist_name in checklist_names:
        
        checklist_details=get_checklist_detail(checklist_name.get('dc_installation_checklist'))
        for checklist_detail in checklist_details:
          data.append(checklist_detail)       

      message={
        'data':data
        }      
      return message

def get_checklist_detail(checklist_name):
  print('checklist_name',checklist_name)
  data=[]
  checklist=frappe.get_doc('DC Installation Checklist', checklist_name)
  # checklist_details= checklist.get('dc_installation_checklist_detail')
  for row in checklist.dc_installation_checklist_detail:
    data.append({
      'checklist':checklist_name,
      'activity':row.activity,
      'description':row.description,
      'is_checked':row.is_checked
    })
  return data