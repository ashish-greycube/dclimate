import frappe
from frappe.modules.import_file import import_file_by_path
from frappe.utils import get_bench_path
import os
from os.path import join



def after_migrations():
	if(not frappe.db.exists('Role','DC Service Provider')):
		fname="role.json"
		import_folder_path="{bench_path}/{app_folder_path}".format(bench_path=get_bench_path(),app_folder_path='/apps/dclimate/dclimate/import_records')
		make_records(import_folder_path,fname)
	if(frappe.db.exists('Workspace','DClimate')==None) and frappe.__version__.split('.')[0]=='14' :
		fname="workspace.json"
		import_folder_path="{bench_path}/{app_folder_path}".format(bench_path=get_bench_path(),app_folder_path='/apps/dclimate/dclimate/import_records')
		make_records(import_folder_path,fname)
	update_dashboard_link_for_core_doctype(doctype="Serial No",link_doctype="DC Service Record",link_fieldname="serial_no",group="Reference")	
	update_dashboard_link_for_core_doctype(doctype="Serial No",link_doctype="DC Service Out of Warranty",link_fieldname="serial_no",group="Reference")
	update_dashboard_link_for_core_doctype(doctype="Serial No",link_doctype="DC Campaign Completion Form",link_fieldname="serial_no",group="Reference")	

	# if(not frappe.db.exists({"doctype":'Custom DocPerm',
	# 													"role":'DC Service Provider'})):
	# 	fname="custom_docperm.json"
	# 	import_folder_path="{bench_path}/{app_folder_path}".format(bench_path=get_bench_path(),app_folder_path='/apps/dclimate/dclimate/import_records')
	# 	make_records(import_folder_path,fname)

	# if(not frappe.db.exists('Workflow','DC Service Record')):
	# fname="workflow.json"
	# import_folder_path="{bench_path}/{app_folder_path}".format(bench_path=get_bench_path(),app_folder_path='/apps/dclimate/dclimate/import_records')
	# make_records(import_folder_path,fname)

	# if(not frappe.db.exists('User','florida_sp@test.com')):
	# 	fname="user.json"
	# 	import_folder_path="{bench_path}/{app_folder_path}".format(bench_path=get_bench_path(),app_folder_path='/apps/dclimate/dclimate/import_records')
	# 	make_records(import_folder_path,fname)		

def make_records(path, fname):
	if os.path.isdir(path):
		import_file_by_path("{path}/{fname}".format(path=path, fname=fname))

def update_dashboard_link_for_core_doctype(
	doctype, link_doctype, link_fieldname, group=None
):
	try:
		d = frappe.get_doc("Customize Form")
		if doctype:
			d.doc_type = doctype
		d.run_method("fetch_to_customize")
		for link in d.get("links"):
			if (
				link.link_doctype == link_doctype
				and link.link_fieldname == link_fieldname
			):
				# found so just return
				return
		d.append(
			"links",
			dict(
				link_doctype=link_doctype,
				link_fieldname=link_fieldname,
				table_fieldname=None,
				group=group,
			),
		)
		d.run_method("save_customization")
		frappe.clear_cache()
	except Exception:
		frappe.log_error(frappe.get_traceback())		