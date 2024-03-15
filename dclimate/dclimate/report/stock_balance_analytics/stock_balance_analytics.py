# Copyright (c) 2024, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.report.stock_balance.stock_balance import (
    execute as _execute,
)

from frappe.utils.dateutils import get_dates_from_timegrain, getdate
from frappe.utils import add_days, add_to_date, unique, add_months, get_last_day

HIDDEN_COLUMNS = (
    "opening_qty",
    "opening_val",
    "bal_qty",
    "bal_val",
    "in_qty",
    "in_val",
    "out_qty",
    "out_val",
    "val_rate",
)

STEPS = {"Half Yearly": 6, "Quarterly": 3, "Monthly": 1}


def get_columns_for_timegrain(columns, timegrains, filters):
    tg_columns = []
    fields = (
        "opening_qty",
        "opening_val",
        "bal_qty",
        "bal_val",
    )

    def _get_label(timegrain, label):
        if filters.timegrain == "Yearly":
            return label
        return " - ".join(unique(x.strftime("%b") for x in timegrain)) + " " + label

    for idx, t in enumerate(timegrains, start=1):
        for f in fields:
            c = next(filter(lambda x: x["fieldname"] == f, columns))
            tg_columns.append(
                {
                    **c,
                    **{
                        "fieldname": c["fieldname"] + "_{}".format(idx),
                        "label": _get_label(t, c["label"]),
                        "width": 130,
                    },
                }
            )

    return tg_columns


def get_dates_for_timegrain(filters):
    if filters.timegrain == "Yearly":
        return [(filters.from_date, filters.to_date)]
    else:
        step = STEPS.get(filters.timegrain)
        out = []
        for d in range(0, 12, step):
            t = add_months(filters.from_date, d)
            out.append((t, get_last_day(add_months(t, step - 1))))
        return out


def execute(filters=None):
    results = {}

    from_date, to_date = frappe.db.get_value(
        "Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"]
    )
    filters.from_date = from_date
    filters.to_date = to_date
    erpnext_columns, erpnext_data = _execute(filters)

    for d in erpnext_data:
        results[(d.item_code, d.warehouse)] = d

    timegrain_dates = get_dates_for_timegrain(filters)

    # Get data for each date range and update results dict
    for idx, d in enumerate(timegrain_dates, start=1):
        filters.from_date, filters.to_date = d
        _, data = _execute(filters)
        for r in data:
            item_wh = (r.item_code, r.warehouse)
            if item_wh in results:
                results[item_wh].update(
                    {
                        f"bal_qty_{idx}": r.bal_qty,
                        f"bal_val_{idx}": r.bal_val,
                        f"opening_qty_{idx}": r.opening_qty,
                        f"opening_val_{idx}": r.opening_val,
                    }
                )
            else:
                suffix = idx == 1 and "" or f"_{idx-1}"
                results[item_wh].update(
                    {
                        f"opening_qty_{idx}": results[item_wh][f"bal_qty" + suffix],
                        f"opening_val_{idx}": results[item_wh][f"bal_val" + suffix],
                        f"bal_qty_{idx}": results[item_wh][f"bal_qty" + suffix],
                        f"bal_val_{idx}": results[item_wh][f"bal_val" + suffix],
                    }
                )
    consolidated_data = list(results.values())

    erpnext_columns[5:5] = get_columns_for_timegrain(
        erpnext_columns, timegrains=timegrain_dates, filters=filters
    )

    if not filters.show_original_columns:
        for c in erpnext_columns:
            if c["fieldname"] in HIDDEN_COLUMNS:
                c["hidden"] = 1

    return erpnext_columns, consolidated_data
