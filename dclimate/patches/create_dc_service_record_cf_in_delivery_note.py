import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    print("Creating fields for Dclimate service record in Delivery note:")
    custom_fields = {
        "Delivery Note": [
            dict(
                fieldname="dc_service_record_cf",
                label="DC Service Record",
                fieldtype="Link",
                options="DC Service Record",
                insert_after="dc_service_out_of_warranty_cf",
            )
        ]
    }

    create_custom_fields(custom_fields, update=True)