import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    print("Creating fields for Truck VIN in Sales Order Item:")
    custom_fields = {
        "Sales Order Item": [
            dict(
                fieldname="truck_vin_cf",
                label="Truck VIN",
                fieldtype="Small Text",
                allow_on_submit="1",
                translatable=0,
                insert_after="ensure_delivery_based_on_produced_serial_no",
            )
        ]
     
    }
    create_custom_fields(custom_fields, update=True)


    