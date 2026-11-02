# Odoo Sale Product Set Layout

Odoo 19.0 addon by **Biricon IT Services GmbH** (AGPL-3).

| Module | Description |
|---|---|
| [sale_product_set_layout](sale_product_set_layout/) | Insert product sets (bills of materials) into quotations as a section, choose per set how prices are printed (every price / set total only / one summary line) and hide lines in reports (e.g. price corrections). |

## What it does

- *Add set* in a quotation creates a section named after the set and puts the set lines below it.
- Each set has a **print mode**: every line with its price, lines without prices and only the set total, or just one line with the set total. The layout is carried over to the invoice and the customer portal.
- Lines can be marked **hidden**: they count for the totals but are not printed (for example price corrections). A set line can also carry a **fixed price** instead of the pricelist price.

## Requirements

- Odoo 19.0
- `sale_product_set` from [OCA/sale-workflow](https://github.com/OCA/sale-workflow) (branch 19.0)
- `product_set` from [OCA/product-attribute](https://github.com/OCA/product-attribute) (branch 19.0)

## Installation

1. Put `sale_product_set`, `product_set` and `sale_product_set_layout` into the addons path.
   On a production system link only these modules into a separate directory instead of adding
   the complete OCA repositories: some OCA modules are installed automatically (`auto_install`)
   once their dependencies exist.
2. Update the apps list and install *Sale Product Set Layout*.

## Tests

```
odoo-bin -d <test database> -i sale_product_set_layout --test-enable --test-tags=/sale_product_set_layout --stop-after-init
```

## Notes

Hidden lines are invisible on printed documents. Check whether this is compatible with the
invoicing rules of your country. Details are in the [module README](sale_product_set_layout/README.rst).
