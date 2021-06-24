// Copyright (c) 2021, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('DC Service Record', {
	setup: function(frm) {
		frm.set_query('serial_no',()=>{
			return {
				filters:{
					"status": "Delivered",
					"installation__note_cf":["not in",[undefined]]
				}
			}
		})
		frappe.db.get_single_value('DClimate Settings', 'job_codes_item_group')
    .then(job_codes_item_group => {
				console.log(job_codes_item_group)
				frm.set_query('job_code','job_codes',()=>{
					return {
						filters:{
							"item_group": job_codes_item_group
						}
					}
				})				
    })		
		frm.set_query("technician", function() {
			if (frm.doc.service_by_supplier) {
				return {
					query: 'frappe.contacts.doctype.contact.contact.contact_query',
					filters: {
						link_doctype: "Supplier",
						link_name: frm.doc.service_by_supplier
					}
				};
			}
		});
	},
	serial_no: function(frm){
		let serial_no=frm.doc.serial_no
		if (serial_no) {
				frappe.db.get_value("Serial No",serial_no,'installation__note_cf')
					.then((r)=>{
						let installation__note_cf=r.message.installation__note_cf;
						if (installation__note_cf) {
							frappe.db.get_value('Installation Note',installation__note_cf,['truck_vin_cf','truck_number_cf'])
								.then((r)=>{
									if(r.message){
									let truck_vin_cf=r.message.truck_vin_cf;
									let truck_number_cf=r.message.truck_number_cf;
									if (truck_vin_cf) {
										frm.set_value('truck_vin',truck_vin_cf)
									}
									if (truck_number_cf) {
										frm.set_value('truck_number',truck_number_cf)
									}
								}
								})
						}
					})
		}
	},
	parts_warranty_expiry_date: function(frm){
		let parts_warranty_expiry_date=frm.doc.parts_warranty_expiry_date
		const today = frappe.datetime.get_today();
		if (parts_warranty_expiry_date && parts_warranty_expiry_date<today) {
			frm.set_value('parts_warranty_status','Warranty Expired')
		}else if(parts_warranty_expiry_date && parts_warranty_expiry_date >= today){
			frm.set_value('parts_warranty_status','Under Warranty')
		}
	},
	labor_warranty_expiry_date: function(frm){
		let labor_warranty_expiry_date=frm.doc.labor_warranty_expiry_date
		const today = frappe.datetime.get_today();
		if (labor_warranty_expiry_date && labor_warranty_expiry_date<today) {
			frm.set_value('labor_warranty_status','Warranty Expired')
		}else if(labor_warranty_expiry_date && labor_warranty_expiry_date >= today){
			frm.set_value('labor_warranty_status','Under Warranty')
		}
	}	
});
