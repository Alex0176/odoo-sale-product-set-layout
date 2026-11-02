# Copyright 2026 Biricon IT Services GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_move_lines_to_report(self):
        return super()._get_move_lines_to_report().filtered(lambda line: not line.hide_in_report)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hide_in_report = fields.Boolean(
        string="Hidden in report",
        help="The line counts for the totals but is not printed on the invoice.",
    )

    def _get_aml_vals(self, hide_taxes):
        res = super()._get_aml_vals(hide_taxes)
        res["hide_in_report"] = self.hide_in_report
        return res

    def _get_detailed_lines(self, children_lines, direct_children_lines, subsection_lines):
        res = super()._get_detailed_lines(children_lines, direct_children_lines, subsection_lines)
        return [vals for vals in res if not vals.get("hide_in_report")]

    def _get_subsection_lines(self, subsection_line, children_lines):
        res = super()._get_subsection_lines(subsection_line, children_lines)
        return [vals for vals in res if not vals.get("hide_in_report")]
