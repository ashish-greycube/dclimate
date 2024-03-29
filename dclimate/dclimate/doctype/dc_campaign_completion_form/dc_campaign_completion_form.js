// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('DC Campaign Completion Form', {
	setup: function(frm) {
		frappe.call('dclimate.dclimate.doctype.dc_service_record.dc_service_record.get_job_codes__for_item_group')
		.then(r => {
			let job_codes_item_group=r.message
							frm.set_query('job_code','job_codes',()=>{
								return {
									filters:{
										"item_group": ['descendants of',job_codes_item_group]
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
	supplier_address: function (frm) {
		if (frm.doc.supplier_address) {
			erpnext.utils.get_address_display(frm, "supplier_address",
				"supplier_address_display", true);
		}
	},
	service_by_supplier: function (frm) {
		if (frm.doc.service_by_supplier) {
			// frappe.db.get_list('Dynamic Link', {
			// 	fields: ['parent'],
			// 	filters: {
			// 		link_doctype: 'Supplier',
			// 		link_name: frm.doc.service_by_supplier,
			// 		parentfield : 'links',
			// 		parenttype :'Address'						
			// 	}
			// }).then(records => {
			// 	if (records.length > 0) {
			// 		let address_list = []
			// 		records.forEach(record => {
			// 			address_list.push(record.parent)
			// 		});
			// 		frm.set_query('supplier_address', () => {
			// 			return {
			// 				filters: {
			// 					name: ['in', address_list]
			// 				}
			// 			}
			// 		})
			// 	}
			// })dclimate/dclimate/dclimate/doctype/dc_campaign_completion_form/dc_campaign_completion_form.py
			frappe.call({
				method: 'dclimate.dclimate.doctype.dc_campaign_completion_form.dc_campaign_completion_form.get_service_by_supplier',
				args: {
					"link_doctype": 'Supplier',
					"link_name": frm.doc.service_by_supplier,
					"parentfield" : 'links',
					"parenttype" :'Address'
				},
				callback: (r) => {
					// on success
					console.log(r)
					let records=r.message
					if (records.length > 0) {
						let address_list = []
						records.forEach(record => {
							address_list.push(record.parent)
						});
						frm.set_query('supplier_address', () => {
							return {
								filters: {
									name: ['in', address_list]
								}
							}
						})
					}				
				},
				error: (r) => {
				}
			})			
		}
	},	
	serial_no: function(frm){
		let serial_no=frm.doc.serial_no
		if (serial_no) {
				frappe.db.get_value("Serial No",serial_no,'installation__note_cf')
					.then((r)=>{
						let installation__note_cf=r.message.installation__note_cf;
						if (installation__note_cf) {
							frappe.db.get_value('Installation Note',installation__note_cf,['truck_vin_cf','truck_number_cf','customer'])
								.then((r)=>{
									if(r.message){
									let truck_vin_cf=r.message.truck_vin_cf;
									let truck_number_cf=r.message.truck_number_cf;
									let customer=r.message.customer;
									if (truck_vin_cf) {
										frm.set_value('truck_vin',truck_vin_cf)
									}
									if (truck_number_cf) {
										frm.set_value('truck_number',truck_number_cf)
									}
									if (customer) {
										frm.set_value('customer',customer)
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
