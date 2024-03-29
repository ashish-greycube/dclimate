// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance Analytics"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      width: "80",
      options: "Company",
      default: frappe.defaults.get_default("company"),
    },
    {
      fieldname: "fiscal_year",
      label: __("Fiscal Year"),
      fieldtype: "Link",
      options: "Fiscal Year",
      default: frappe.sys_defaults.fiscal_year,
      reqd: 1,
    },
    {
      fieldname: "timegrain",
      label: __("Timegrain"),
      fieldtype: "Select",
      options: "Yearly\nHalf Yearly\nQuarterly\nMonthly",
      reqd: 1,
    },
    {
      fieldname: "item_group",
      label: __("Item Group"),
      fieldtype: "Link",
      width: "80",
      options: "Item Group",
    },
    {
      fieldname: "item_code",
      label: __("Item"),
      fieldtype: "Link",
      width: "80",
      options: "Item",
      get_query: function () {
        return {
          query: "erpnext.controllers.queries.item_query",
        };
      },
    },
    {
      fieldname: "warehouse",
      label: __("Warehouse"),
      fieldtype: "Link",
      width: "80",
      options: "Warehouse",
      get_query: () => {
        let warehouse_type =
          frappe.query_report.get_filter_value("warehouse_type");
        let company = frappe.query_report.get_filter_value("company");

        return {
          filters: {
            ...(warehouse_type && { warehouse_type }),
            ...(company && { company }),
          },
        };
      },
    },
    {
      fieldname: "warehouse_type",
      label: __("Warehouse Type"),
      fieldtype: "Link",
      width: "80",
      options: "Warehouse Type",
    },
    {
      fieldname: "include_uom",
      label: __("Include UOM"),
      fieldtype: "Link",
      options: "UOM",
    },
    {
      fieldname: "show_variant_attributes",
      label: __("Show Variant Attributes"),
      fieldtype: "Check",
    },
    {
      fieldname: "show_stock_ageing_data",
      label: __("Show Stock Ageing Data"),
      fieldtype: "Check",
    },
    {
      fieldname: "ignore_closing_balance",
      label: __("Ignore Closing Balance"),
      fieldtype: "Check",
      default: 1,
    },
    {
      fieldname: "show_original_columns",
      label: __("Show Original Columns"),
      fieldtype: "Check",
      default: 0,
    },
  ],

  formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);

    if (column.fieldname.startsWith("opening_qty")) {
      console.log(value);
      value = value.replace(
        "style='text-align: right'",
        "style='text-align: right;background-color:#efefef;margin:-2px -2px'"
      );
    }
    if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
      value = "<span style='color:red'>" + value + "</span>";
    } else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
      value = "<span style='color:green'>" + value + "</span>";
    }

    return value;
  },
};

erpnext.utils.add_inventory_dimensions("Stock Balance", 8);
