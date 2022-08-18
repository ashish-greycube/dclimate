# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from erpnext.accounts.report.profit_and_loss_statement.profit_and_loss_statement import (
    get_period_list,
    get_report_summary,
    get_chart_data,
    get_data,
    get_columns,
    get_net_profit_loss,
)


def execute(filters=None):
    period_list = get_period_list(
        filters.from_fiscal_year,
        filters.to_fiscal_year,
        filters.period_start_date,
        filters.period_end_date,
        filters.filter_based_on,
        filters.periodicity,
        company=filters.company,
    )

    income = get_data(
        filters.company,
        "Income",
        "Credit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )

    expense = get_data(
        filters.company,
        "Expense",
        "Debit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )

    if filters.get("income_account"):
        tmp = list(
            filter(lambda x: x.get("account") == filters.get("income_account"), income)
        )
        tmp[0]["parent_account"] = income[0]["account"]
        for d in income:
            for period in period_list:
                d[period.key] = tmp[0][period.key]
        income = [income[0]] + tmp + income[-2:]

    if filters.get("expense_account"):
        tmp = list(
            filter(
                lambda x: x.get("account") == filters.get("expense_account"), expense
            )
        )
        tmp[0]["parent_account"] = expense[0]["account"]
        for d in expense:
            for period in period_list:
                d[period.key] = tmp[0][period.key]
        expense = [expense[0]] + tmp + expense[-2:]

    net_profit_loss = get_net_profit_loss(
        income, expense, period_list, filters.company, filters.presentation_currency
    )

    data = []
    data.extend(income or [])
    data.extend(expense or [])
    if net_profit_loss:
        data.append(net_profit_loss)

    columns = get_columns(
        filters.periodicity, period_list, filters.accumulated_values, filters.company
    )

    chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

    currency = filters.presentation_currency or frappe.get_cached_value(
        "Company", filters.company, "default_currency"
    )

    report_summary = get_report_summary(
        period_list,
        filters.periodicity,
        income,
        expense,
        net_profit_loss,
        currency,
        filters,
    )

    return columns, data, None, chart, report_summary
