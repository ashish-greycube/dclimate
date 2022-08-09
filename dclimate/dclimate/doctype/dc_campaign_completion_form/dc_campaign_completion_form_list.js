frappe.listview_settings['DC Campaign Completion Form'] = {
  has_indicator_for_draft: 1,
	add_fields: ["status"],
	get_indicator: function(doc) {
		var status_color = {
			"Open": "orange",
			"Finished": "green",
		};
		return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
	}
};