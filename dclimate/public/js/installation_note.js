frappe.ui.form.on('Installation Note', {
    onload_post_render:function(frm){
        make_child_table_colms_readonly(frm)
       
    },
    // before_save: function(frm){
    //     frm.doc.truck_vin_cf=frm.doc.pick_truck_vin_cf

    // },
    pick_truck_vin_cf: function(frm){
        frm.set_value('truck_vin_cf', frm.doc.pick_truck_vin_cf)
    },
    sales_order_cf: function(frm){
        set_customer_end_customer_for_so(frm)
    },
    check_all_cf: function(frm){
        var checklist_items = frm.doc.dc_installation_checklist_detail_cf || [];
        for (let index in checklist_items){
            if (checklist_items[index].is_checked==0){
                frappe.model.set_value(checklist_items[index].doctype, checklist_items[index].name, "is_checked", 1)
            }
        }      
        frm.refresh_field('dc_installation_checklist_detail_cf')
    },
    refresh : function(frm){
        if (frm.doc.sales_order_cf && frm.doc.items.length>0) {
            set_options_for_truck_vin(frm)
        }
        $('[data-fieldname="dc_installation_checklist_detail_cf"] button.grid-add-row').hide()
        make_child_table_colms_readonly(frm)
    },
    setup:function(frm){
        // frm.set_query('pick_serial_no_cf', 'items', () => {
        //     return {
        //         filters: {
        //             status:[ '!=','Delivered']
        //         }
        //     }
        // })

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
        if (row.item_code && frm.doc.sales_order_cf) {
            set_options_for_truck_vin(frm)
        }
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
    },
    pick_serial_no_cf:function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
            row.serial_no=row.pick_serial_no_cf
            frm.refresh_field('items');
    }
})

function set_customer_end_customer_for_so(frm){
    if (frm.doc.sales_order_cf) {
            frappe.db.get_value('Sales Order', frm.doc.sales_order_cf, ['customer', 'end_customer_cf'])
            .then(r => {
                let values = r.message;
                frm.set_value('customer', values.customer)
                frm.set_value('end_customer_cf', values.end_customer_cf)
            })            
    }
}

async function set_options_for_truck_vin(frm){
    let valid_fields=[]
    let items=frm.doc.items
    let so=frm.doc.sales_order_cf
    for (let index = 0; index < items.length; index++) {
        let item = items[index].item_code;
        if (item==undefined) {
            return
        }
        let truck_vin_cifs=await fetch_truck_vin_cf_from_so_item(so,item)
        truck_vin_cifs=truck_vin_cifs.split("\n")
        for (let index = 0; index < truck_vin_cifs.length; index++) {
            let truck_vin_cif = truck_vin_cifs[index];
            if (truck_vin_cif!='') {
                valid_fields.push({"label": truck_vin_cif, "value":truck_vin_cif})
            }
        }
    }
    frm.fields_dict.pick_truck_vin_cf.set_data(valid_fields)
}

function fetch_truck_vin_cf_from_so_item(so,item) {
//    return frappe.db.get_list('Sales Order Item', {
//         fields: ['truck_vin_cf'],
//         filters: {
//             parent: so,
//             item_code:item
//         }
//     }).then(records => {
//         if (records && records[0])  {
//             return records[0].truck_vin_cf
//         } else {
//             return ''
//         }
        
//     })    
    
    return frappe.call('dclimate.installation_note_hook.get_truck_vin_cf_from_so_item', {
        so_item: {'so':so,'item':item}
    }).then(r => {
        console.log(r.message)
        if (r.message) {
            return r.message
        } else {
            return ''
        }
    })

}


function make_child_table_colms_readonly(frm) {
    if (frappe.user.has_role('Installer')) {
        frm.fields_dict.dc_installation_checklist_detail_cf.grid.update_docfield_property('activity', 'read_only', 1);
        frm.fields_dict.dc_installation_checklist_detail_cf.grid.update_docfield_property('description', 'read_only', 1);
        $('[data-fieldname="dc_installation_checklist_detail_cf"] button.grid-add-row').hide()

    }   
}