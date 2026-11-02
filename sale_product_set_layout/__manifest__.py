# Copyright 2026 Biricon IT Services GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Set Layout",
    "summary": "Insert product sets (bills of materials) into quotations as a section, "
    "choose per set how prices are printed and hide lines in reports",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "author": "Biricon IT Services GmbH",
    "website": "https://github.com/Alex0176/odoo-sale-product-set-layout",
    "license": "AGPL-3",
    "depends": ["sale_management", "sale_product_set", "account"],
    "data": [
        "views/product_set_views.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "wizard/sale_product_set_wizard_views.xml",
    ],
    "installable": True,
}
