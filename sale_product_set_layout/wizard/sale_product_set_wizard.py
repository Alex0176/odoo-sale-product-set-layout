# Copyright 2026 Biricon IT Services GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models

from ..models.product_set import PRINT_MODE_FLAGS, PRINT_MODES


class SaleProductSetWizard(models.TransientModel):
    _inherit = "sale.product.set.wizard"

    # separate computes: a value passed explicitly for one field must not reset the others
    insert_as_section = fields.Boolean(
        compute="_compute_insert_as_section", store=True, readonly=False
    )
    section_name = fields.Char(compute="_compute_section_name", store=True, readonly=False)
    print_mode = fields.Selection(
        PRINT_MODES, compute="_compute_print_mode", store=True, readonly=False
    )

    @api.depends("product_set_id")
    def _compute_insert_as_section(self):
        for wiz in self:
            wiz.insert_as_section = wiz.product_set_id.insert_as_section if wiz.product_set_id else True

    @api.depends("product_set_id")
    def _compute_print_mode(self):
        for wiz in self:
            wiz.print_mode = wiz.product_set_id.print_mode or "detailed"

    @api.depends("product_set_id", "quantity")
    def _compute_section_name(self):
        for wiz in self:
            name = wiz.product_set_id.name or ""
            if name and wiz.quantity and wiz.quantity != 1:
                name = "%s × %s" % (("%g" % wiz.quantity).replace(".", ","), name)
            wiz.section_name = name

    def _prepare_order_lines(self):
        if not self.insert_as_section:
            return super()._prepare_order_lines()
        sequence = self._get_max_sequence() + 1
        collapse_prices, collapse_composition = PRINT_MODE_FLAGS[self.print_mode or "detailed"]
        order_lines = [
            Command.create(
                {
                    "display_type": "line_section",
                    "name": self.section_name or self.product_set_id.name,
                    "sequence": sequence,
                    "collapse_prices": collapse_prices,
                    "collapse_composition": collapse_composition,
                }
            )
        ]
        for set_line in self._get_lines():
            sequence += 1
            values = set_line.prepare_sale_order_line_values(
                self.order_id, self.quantity, sequence
            )
            # sections inside the set become subsections of the set section
            if values.get("display_type") == "line_section":
                values["display_type"] = "line_subsection"
            order_lines.append(Command.create(values))
        return order_lines
