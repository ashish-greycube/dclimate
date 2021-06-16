frappe.ui.form.on('Installation Note', {
    dc_installation_checklist_cf: function (frm) {

    },
    onload_post_render: function (frm) {
        if (frm.doc.dc_installation_checklist_cf == undefined || frm.doc.dc_installation_checklist_cf == '') {
            var items = frm.doc.items || [];
            processItems(items, frm)
            console.log('end of refresh', cur_frm.doc.dc_installation_checklist_detail_cf)

        }
    }
})

async function processItems(items, frm) {
    for (const item of items) {
        console.log('i')
        await get_item_details(item.item_code, frm)
    }
    console.log('outside for loop')
}

function get_item_details(item_code, frm) {
    return new Promise((resolve, reject) =>
        frappe.db.get_value('Item', item_code, 'default_installation_checklist_cf')
        .then(r => {
            console.log(r.message.default_installation_checklist_cf)
            let default_installation_checklist_cf = r.message.default_installation_checklist_cf
            if (default_installation_checklist_cf != null) {
                console.log('default_installation_checklist_cf', default_installation_checklist_cf)
                // frm.set_value('dc_installation_checklist_detail_cf', default_installation_checklist_cf)
                //     .then(() => {
                //         // do something after value is set
                //         frm.refresh_field('dc_installation_checklist_detail_cf')
                //         resolve(r.message)


                //     })
            }

        })
    )
}
frappe.ui.form.on('Installation Note Item', {
    item_code: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];

        console.log(d.item_code)
    }
})