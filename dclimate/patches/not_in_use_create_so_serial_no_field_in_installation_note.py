import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    print("Creating fields for SO in Installation note:")
    custom_fields = {
        "Installation Note": [
            dict(
                fieldname="sales_order_cf",
                label="Sales Order",
                fieldtype="Link",
                options="Sales Order",
                insert_after="naming_series",
            ),
            dict(
                fieldname="pick_truck_vin_cf",
                label="Pick Truck VIN",
                fieldtype="Autocomplete",
                insert_after="truck_vin_cf",
            )            
        ],
        "Installation Note Item": [
            dict(
                fieldname="pick_serial_no_cf",
                label="Pick Serial No",
                fieldtype="Link",
                options="Serial No",
                insert_after="item_code",
                in_list_view=1,

            )
        ]        
    }

    create_custom_fields(custom_fields, update=True)
    # print('---'*10)
    # serial_no_read_only =make_property_setter("Installation Note Item", "serial_no", "read_only", 1, "Check")
    # print('serial_no_read_only',serial_no_read_only)
    # serial_no_in_list_view=make_property_setter("Installation Note Item", "serial_no", "in_list_view", 0, "Check")
    # print('serial_no_in_list_view',serial_no_in_list_view)
    # serial_no_label =make_property_setter("Installation Note Item", "serial_no", "label", "Final Serial No", "Data")
    # print('serial_no_label',serial_no_label)
    # truck_vin_cf_read_only=make_property_setter("Installation Note", "truck_vin_cf", "read_only", 1, "Check")
    # print(truck_vin_cf_read_only,truck_vin_cf_read_only)
    # truck_vin_cf_label=make_property_setter("Installation Note", "truck_vin_cf", "label", "Final Truck VIN", "Data")
    # print('truck_vin_cf_label',truck_vin_cf_label)
    # frappe.db.commit()
    # print('---'*10)
    # installation_note_item = frappe.qb.DocType("Installation Note Item")
    # frappe.qb.update(installation_note_item).set(installation_note_item.in_list_view, 0).run()

#     def make_property_setter(
# 	doctype,
# 	fieldname,
# 	property,
# 	value,
# 	property_type,
# 	for_doctype=False,
# 	validate_fields_for_doctype=True,
# )