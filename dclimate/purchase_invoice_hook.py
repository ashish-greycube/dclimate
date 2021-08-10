import frappe
from frappe import _

def validate_supplier_against_dc_service_record(self,method):
	if self.dc_service_record_cf:
		service_by_supplier = frappe.db.get_value('DC Service Record', self.dc_service_record_cf, 'service_by_supplier')
		if service_by_supplier!=self.supplier:
			frappe.throw(msg=_("Supplier value should be {0} , same as suppiler in DC service record {1}"
			.format(frappe.bold(service_by_supplier),self.dc_service_record_cf)),title='Supplier value error')