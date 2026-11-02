# Copyright 2026 Biricon IT Services GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_lines_to_report(self):
        return super()._get_order_lines_to_report().filtered(lambda line: not line.hide_in_report)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    hide_in_report = fields.Boolean(
        string="Hidden in report",
        copy=True,
        help="The line counts for the totals but is neither printed nor shown in the "
        "customer portal. The flag is passed on to the invoice.",
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if self.hide_in_report:
            res["hide_in_report"] = True
        return res
