// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('DC Campaign', {
	sync_dc_campaign_completion_form:function(frm) {
		frm.call({
			doc: frm.doc,
			method: 'sync_dc_campaign_completion_form',
			freeze: true,
			callback: () => {
				frappe.msgprint(__('DC Campaign Serial No is updated.'));
			}			
		});
	},
	setup: function(frm) {
		frm.set_query('serial_no', 'dc_campaign_serial_no', () => {
			return {
				filters: {
					status:['in',['Active',	'Inactive',	'Delivered','Expired']] 
				}
			}
		})		
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
	}
});

frappe.ui.form.on('DC Service Record Job Codes Detail', {
    job_code:function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if (row.job_code ) {
            return frappe.call({
				method: "dclimate.dclimate.doctype.dc_service_record.dc_service_record.get_hours_for_job_codes",
				args: {
					"job_code": row.job_code,
				},
				callback: function(r) {
					if(!r.exc && r.message) {
						frappe.model.set_value(cdt, cdn, "hours", flt(r.message));
					}
				}
			});          
        }
    }
})

frappe.ui.form.on('DC Campaign Serial No', {
    before_dc_campaign_serial_no_remove:function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if (row.dc_campaign_completion_form ) {
            return frappe.db.get_value('DC Campaign Completion Form', row.dc_campaign_completion_form, ['status', 'docstatus'])
			.then(r => {
				let values = r.message;
				console.log(values.status, values.docstatus)
				if (values.docstatus==1) {
					frappe.throw(__('Row #{0} : DC Campaign Completion Form <b>{1}</b>, docstatus is <b>submitted.</b> Hence cannot remove it.',[row.idx,row.dc_campaign_completion_form]))
					
				}
			})     
        }
    }
})