# Copyright 2026 Biricon IT Services GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleProductSetLayout(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        Product = cls.env["product.product"]
        common = {"type": "service", "invoice_policy": "order", "taxes_id": [(5, 0, 0)]}
        cls.p_main = Product.create(dict(common, name="Main part", list_price=100.0))
        cls.p_extra = Product.create(dict(common, name="Extra part", list_price=50.0))
        cls.p_corr = Product.create(dict(common, name="Price correction", list_price=0.0))
        cls.partner = cls.env["res.partner"].create({"name": "Set customer"})
        cls.pset = cls.env["product.set"].create(
            {
                "name": "Measuring kit",
                "print_mode": "total_only",
                "set_line_ids": [
                    (0, 0, {"product_id": cls.p_main.id, "quantity": 1, "sequence": 1}),
                    (0, 0, {"display_type": "line_section", "name": "Options", "sequence": 2}),
                    (0, 0, {"product_id": cls.p_extra.id, "quantity": 1, "sequence": 3}),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.p_corr.id,
                            "quantity": 1,
                            "sequence": 4,
                            "fixed_price": True,
                            "price_unit": -20.0,
                            "hide_in_report": True,
                        },
                    ),
                ],
            }
        )

    def _new_order(self):
        return self.env["sale.order"].create({"partner_id": self.partner.id})

    def _add_set(self, order, quantity=1.0, **vals):
        wiz = self.env["sale.product.set.wizard"].create(
            dict({"order_id": order.id, "product_set_id": self.pset.id, "quantity": quantity}, **vals)
        )
        wiz.add_set()
        return order

    def test_insert_as_section_with_print_mode(self):
        order = self._add_set(self._new_order(), quantity=2)
        section = order.order_line.filtered(lambda l: l.display_type == "line_section")
        self.assertEqual(len(section), 1)
        self.assertEqual(section.name, "2 × Measuring kit")
        self.assertTrue(section.collapse_prices)
        self.assertFalse(section.collapse_composition)
        # a section inside the set becomes a subsection
        self.assertEqual(
            order.order_line.filtered(lambda l: l.display_type == "line_subsection").name, "Options"
        )
        # totals include the hidden correction: 2 * (100 + 50 - 20)
        self.assertAlmostEqual(order.amount_untaxed, 260.0)
        self.assertAlmostEqual(section._get_section_totals("price_subtotal"), 260.0)

    def test_hidden_line_not_reported(self):
        order = self._add_set(self._new_order(), print_mode="detailed")
        hidden = order.order_line.filtered("hide_in_report")
        self.assertEqual(hidden.product_id, self.p_corr)
        self.assertAlmostEqual(hidden.price_unit, -20.0)
        self.assertNotIn(hidden, order._get_order_lines_to_report())
        self.assertIn(
            order.order_line.filtered(lambda l: l.product_id == self.p_main), order._get_order_lines_to_report()
        )

    def test_summary_mode(self):
        order = self._add_set(self._new_order(), print_mode="summary")
        section = order.order_line.filtered(lambda l: l.display_type == "line_section")
        self.assertTrue(section.collapse_composition)
        self.assertFalse(section.collapse_prices)
        # only the section is printed
        self.assertEqual(order._get_order_lines_to_report(), section)

    def test_without_section(self):
        order = self._add_set(self._new_order(), insert_as_section=False)
        self.assertFalse(order.order_line.filtered(lambda l: l.display_type == "line_section" and l.name == "Measuring kit"))
        self.assertAlmostEqual(order.amount_untaxed, 130.0)

    def test_invoice_keeps_hidden_flag(self):
        order = self._add_set(self._new_order(), print_mode="detailed")
        order.action_confirm()
        invoice = order._create_invoices()
        hidden = invoice.invoice_line_ids.filtered("hide_in_report")
        self.assertEqual(hidden.product_id, self.p_corr)
        self.assertAlmostEqual(invoice.amount_untaxed, 130.0)
        self.assertNotIn(hidden, invoice._get_move_lines_to_report())
        section = invoice.invoice_line_ids.filtered(lambda l: l.display_type == "line_section")
        self.assertAlmostEqual(section.get_section_subtotal(), 130.0)

    def test_invoice_collapsed_prices_hides_line(self):
        order = self._add_set(self._new_order(), print_mode="total_only")
        order.action_confirm()
        invoice = order._create_invoices()
        section = invoice.invoice_line_ids.filtered(lambda l: l.display_type == "line_section")
        self.assertTrue(section.collapse_prices)
        names = [vals["name"] for vals in section._get_child_lines()]
        hidden_name = invoice.invoice_line_ids.filtered("hide_in_report").name
        self.assertNotIn(hidden_name, names)
        # section summary still carries the full amount
        self.assertAlmostEqual(section._get_child_lines()[0]["price_subtotal"], 130.0)

    def test_add_set_to_invoice(self):
        invoice = self.env["account.move"].create({"move_type": "out_invoice", "partner_id": self.partner.id})
        wiz = self.env["account.product.set.wizard"].create(
            {"move_id": invoice.id, "product_set_id": self.pset.id, "quantity": 2}
        )
        wiz.add_set()
        section = invoice.invoice_line_ids.filtered(lambda l: l.display_type == "line_section")
        self.assertEqual(section.name, "2 × Measuring kit")
        self.assertEqual(
            invoice.invoice_line_ids.filtered(lambda l: l.display_type == "line_subsection").name, "Options"
        )
        hidden = invoice.invoice_line_ids.filtered("hide_in_report")
        self.assertEqual(hidden.product_id, self.p_corr)
        self.assertAlmostEqual(hidden.price_unit, -20.0)
        self.assertAlmostEqual(invoice.amount_untaxed, 260.0)
        self.assertNotIn(hidden, invoice._get_move_lines_to_report())

    def test_add_set_with_invoice_line_list_context(self):
        """The line list of the invoice form sends its own context with the button
        (journal_id, default_*, quick_encoding_vals). It must not reach the new lines."""
        invoice = self.env["account.move"].create({"move_type": "out_invoice", "partner_id": self.partner.id})
        # With a default account on the journal and journal_id in the context, the default_get of
        # account.move.line puts a record (not an id) into the defaults; the insert then fails
        # with "can't adapt type 'account.account'".
        income = self.env["account.account"].search(
            [("account_type", "=", "income"), ("company_ids", "in", invoice.company_id.id)], limit=1
        )
        self.assertTrue(income)
        invoice.journal_id.default_account_id = income
        context = {
            "journal_id": invoice.journal_id.id,
            "default_move_type": "out_invoice",
            "default_partner_id": invoice.partner_id.id,
            "default_currency_id": invoice.currency_id.id,
            "default_display_type": "product",
            "quick_encoding_vals": invoice.quick_encoding_vals,
            "move_id": invoice.id,
        }
        wiz = (
            self.env["account.product.set.wizard"]
            .with_context(**context)
            .create({"move_id": invoice.id, "product_set_id": self.pset.id, "quantity": 1})
        )
        wiz.add_set()
        # Same result as from a call without that context.
        plain = self.env["account.move"].create({"move_type": "out_invoice", "partner_id": self.partner.id})
        self.env["account.product.set.wizard"].create(
            {"move_id": plain.id, "product_set_id": self.pset.id, "quantity": 1}
        ).add_set()

        def shape(move):
            return [(line.display_type, line.product_id.id, line.quantity) for line in move.invoice_line_ids]

        self.assertTrue(invoice.invoice_line_ids.filtered(lambda line: line.display_type == "product"))
        self.assertEqual(shape(invoice), shape(plain))
        self.assertEqual(invoice.state, "draft")

    def test_add_set_to_posted_invoice_refused(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [(0, 0, {"product_id": self.p_main.id, "quantity": 1})],
            }
        )
        invoice.action_post()
        wiz = self.env["account.product.set.wizard"].create({"move_id": invoice.id, "product_set_id": self.pset.id})
        with self.assertRaises(UserError):
            wiz.add_set()
