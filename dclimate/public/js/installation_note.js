frappe.ui.form.on('Installation Note', {
    refresh : function(frm){
        $('[data-fieldname="dc_installation_checklist_detail_cf"] button.grid-add-row').hide()
    },
    setup:function(frm){
		frm.set_query('supplier_location_cf', function (doc) {
			return {
				query: 'frappe.contacts.doctype.address.address.address_query',
				filters: {
					link_doctype: 'Supplier',
					link_name: doc.installed_by_supplier_cf
				}
			}
		});        
    },
    dc_installation_checklist_multi_cf: function (frm) {
        if (frm.doc.dc_installation_checklist_multi_cf){
			return frappe.call({
				method: "dclimate.installation_note_hook.get_dc_installation_checklist",
				args: {
					"checklist_names": frm.doc.dc_installation_checklist_multi_cf,
					"items": undefined,
				},
				callback: function(r) {
					if(!r.exc && r.message) {
								if(r.message) {
									frm.set_value("dc_installation_checklist_detail_cf", r.message.data);
								}
					}else{
                        frm.set_value("dc_installation_checklist_detail_cf", []);
                    }
				}
			});            
        }
        else{
           
            frm.refresh_field('dc_installation_checklist_detail_cf')
        }
        
    },
    before_submit: function (frm) {
        frm.toggle_reqd('heater_serial_no_cf', frm.doc.docstatus == '0');
        frm.toggle_reqd('truck_number_cf', frm.doc.docstatus == '0');
        frm.toggle_reqd('truck_vin_cf', frm.doc.docstatus == '0');
        frm.toggle_reqd('heater_serial_no_cf', frm.doc.docstatus == '0');
       
        var checklist_items = frm.doc.dc_installation_checklist_detail_cf || [];
        for (let index in checklist_items){
            if (checklist_items[index].is_checked==0){
                frappe.throw({'message':__("'Is Checked' field at <b> row {0} is unchecked </b>. <br>Please check all 'Is Checked' fields in table 'Installation Check List' before submission.",[checklist_items[index].idx]),'title':__('Check List Error')})
            }
        }
    },
    onload_post_render: function (frm) {
        $('[data-fieldname="dc_installation_checklist_detail_cf"] button.grid-add-row').hide()
        if (frm.doc.dc_installation_checklist_multi_cf == undefined || frm.doc.dc_installation_checklist_multi_cf == '') {
            var items = frm.doc.items || [];
			return frappe.call({
				method: "dclimate.installation_note_hook.get_dc_installation_checklist",
				args: {
					"checklist_names": frm.doc.dc_installation_checklist_multi_cf,
					"items": frm.doc.items,
				},
				callback: function(r) {
					if(!r.exc && r.message) {
                        // directly set in doc, so as not to call triggers
                        // frm.fields_dict.dc_installation_checklist_multi_cf.input.value=r.message.default_installation_checklist_cf
                        frm.set_value("dc_installation_checklist_multi_cf", r.message.dc_installation_checklist_multi_cf);
						frm.set_value("dc_installation_checklist_detail_cf", r.message.data);
					}
				}
			}); 
            //async approach
            // processItems(items, frm)

        }
    }
});
async function processItems(items, frm) {
    for (const item of items) {
        await get_item_details(item.item_code, frm)
    }
}
function get_item_details(item_code, frm) {
    return new Promise((resolve, reject) =>
        frappe.db.get_value('Item', item_code, 'default_installation_checklist_cf')
        .then(r => {
            let default_installation_checklist_cf = r.message.default_installation_checklist_cf
            if (default_installation_checklist_cf != null) {
                frm.fields_dict.dc_installation_checklist_multi_cf.input.value=default_installation_checklist_cf
                return frappe.call({
                    method: "dclimate.installation_note_hook.get_dc_installation_checklist",
                    args: {
                        "checklist_names": default_installation_checklist_cf,
                        "items": undefined,
                    },
                    callback: function(r) {
                        if(!r.exc && r.message) {
                                    if(r.message) {
                                        frm.set_value("dc_installation_checklist_detail_cf", r.message.data);
                                    }
                        }
                    }
                });     
                resolve(r.message)
            }
        })
    )
}

frappe.ui.form.on('Installation Note Item', {
    item_code:function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if (row.item_code && (frm.doc.dc_installation_checklist_multi_cf == undefined || frm.doc.dc_installation_checklist_multi_cf == '')) {
            return frappe.call({
				method: "dclimate.installation_note_hook.get_dc_installation_checklist",
				args: {
					"checklist_names": frm.doc.dc_installation_checklist_multi_cf,
					"items": frm.doc.items,
				},
				callback: function(r) {
					if(!r.exc && r.message) {
                        frm.set_value("dc_installation_checklist_multi_cf", r.message.dc_installation_checklist_multi_cf);
                        frm.set_value("dc_installation_checklist_detail_cf", r.message.data);
					}
				}
			});          
        }
    }
})