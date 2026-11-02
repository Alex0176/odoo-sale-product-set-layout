# Copyright 2026 Biricon IT Services GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

PRINT_MODES = [
    ("detailed", "Print every line with its price"),
    ("total_only", "Print the lines without prices, set total only"),
    ("summary", "Print only one line with the set total"),
]

# print mode -> (collapse_prices, collapse_composition) of the section line
PRINT_MODE_FLAGS = {
    "detailed": (False, False),
    "total_only": (True, False),
    "summary": (False, True),
}


class ProductSet(models.Model):
    _inherit = "product.set"

    insert_as_section = fields.Boolean(
        default=True,
        help="When the set is added to a quotation, a section named like the set "
        "is created and the set lines are placed below it.",
    )
    print_mode = fields.Selection(
        PRINT_MODES,
        default="detailed",
        required=True,
        help="How the set is printed on quotations, orders and invoices "
        "(only used when the set is inserted as a section).",
    )


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    hide_in_report = fields.Boolean(
        string="Hidden",
        help="The line is part of the totals but is not printed "
        "(e.g. price corrections).",
    )
    fixed_price = fields.Boolean(
        help="Use the price below instead of the price from the pricelist."
    )
    price_unit = fields.Float(string="Unit Price", digits="Product Price")

    def prepare_sale_order_line_values(self, order, quantity, sequence=0):
        res = super().prepare_sale_order_line_values(order, quantity, sequence=sequence)
        if not self.display_type:
            res["hide_in_report"] = self.hide_in_report
            if self.fixed_price:
                res["price_unit"] = self.price_unit
        return res
