# Copyright 2026 Biricon IT Services GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, exceptions, fields, models


class AccountProductSetWizard(models.TransientModel):
    """Insert a product set into a draft customer invoice (counterpart of the quotation wizard)."""

    _inherit = "product.set.wizard"
    _name = "account.product.set.wizard"
    _description = "Wizard model to add a product set into an invoice"

    move_id = fields.Many2one(
        "account.move",
        string="Invoice",
        required=True,
        ondelete="cascade",
        domain="[('move_type', 'in', ('out_invoice', 'out_refund')), ('state', '=', 'draft')]",
        default=lambda self: self.env.context.get("active_id")
        if self.env.context.get("active_model") == "account.move"
        else None,
    )
    partner_id = fields.Many2one(related="move_id.partner_id", ondelete="cascade")
    insert_as_section = fields.Boolean(
        compute="_compute_insert_as_section", store=True, readonly=False
    )
    section_name = fields.Char(compute="_compute_section_name", store=True, readonly=False)

    @api.depends("product_set_id")
    def _compute_insert_as_section(self):
        for wiz in self:
            wiz.insert_as_section = (
                wiz.product_set_id.insert_as_section if wiz.product_set_id else True
            )

    @api.depends("product_set_id", "quantity")
    def _compute_section_name(self):
        for wiz in self:
            name = wiz.product_set_id.name or ""
            if name and wiz.quantity and wiz.quantity != 1:
                name = "%s × %s" % (("%g" % wiz.quantity).replace(".", ","), name)
            wiz.section_name = name

    def _check_partner(self):
        """Sets restricted to a partner can only be used on invoices of that partner."""
        if not self.product_set_id.partner_id:
            return
        if self.move_id.partner_id != self.product_set_id.partner_id:
            raise exceptions.ValidationError(
                self.env._(
                    "You can use an invoice assigned only to the following partner: %s",
                    self.product_set_id.partner_id.name,
                )
            )

    def _get_max_sequence(self):
        lines = self.move_id.invoice_line_ids
        return max(lines.mapped("sequence") or [0])

    def _prepare_move_lines(self):
        sequence = self._get_max_sequence()
        commands = []
        if self.insert_as_section:
            sequence += 1
            commands.append(
                Command.create(
                    {
                        "display_type": "line_section",
                        "name": self.section_name or self.product_set_id.name,
                        "sequence": sequence,
                    }
                )
            )
        for set_line in self._get_lines():
            sequence += 1
            if set_line.display_type:
                display_type = set_line.display_type
                # sections inside the set become subsections of the set section
                if display_type == "line_section" and self.insert_as_section:
                    display_type = "line_subsection"
                commands.append(
                    Command.create(
                        {"display_type": display_type, "name": set_line.name or "", "sequence": sequence}
                    )
                )
                continue
            values = {
                "display_type": "product",
                "product_id": set_line.product_id.id,
                "quantity": set_line.quantity * self.quantity,
                "sequence": sequence,
                "discount": set_line.discount,
                "hide_in_report": set_line.hide_in_report,
            }
            if set_line.product_uom_id.uom_id:
                values["product_uom_id"] = set_line.product_uom_id.uom_id.id
            if set_line.name:
                values["name"] = set_line.name
            if set_line.fixed_price:
                values["price_unit"] = set_line.price_unit
            commands.append(Command.create(values))
        return commands

    def add_set(self):
        self._check_partner()
        if self.move_id.state != "draft":
            raise exceptions.UserError(
                self.env._("Product sets can only be added to draft invoices.")
            )
        commands = self._prepare_move_lines()
        if commands:
            self.move_id.write({"invoice_line_ids": commands})
        return {"type": "ir.actions.act_window_close"}
