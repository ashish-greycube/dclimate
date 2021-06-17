# Copyright (c) 2021, GreyCube Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class DCInstallationChecklist(Document):
	def autoname(self):
		if self.checklist_name:
			self.name=self.checklist_name
