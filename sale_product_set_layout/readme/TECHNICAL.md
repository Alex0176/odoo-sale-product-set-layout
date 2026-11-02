Extended models and added fields:

| Model | Addition |
|---|---|
| `product.set` | `insert_as_section`, `print_mode` |
| `product.set.line` | `hide_in_report`, `fixed_price`, `price_unit`; `prepare_sale_order_line_values()` passes them to the order line |
| `sale.product.set.wizard` | `insert_as_section`, `section_name`, `print_mode`; `_prepare_order_lines()` builds the section |
| `sale.order` / `sale.order.line` | `hide_in_report`; `_get_order_lines_to_report()` skips hidden lines; `_prepare_invoice_line()` passes the flag on |
| `account.move` / `account.move.line` | `hide_in_report`; `_get_move_lines_to_report()` and the detailed/subsection line helpers skip hidden lines |

The print mode is mapped to the standard section options `collapse_prices`
(*total only*) and `collapse_composition` (*summary*). Sections inside a set are
inserted as subsections (`line_subsection`).

Run the tests with `--test-enable --test-tags=/sale_product_set_layout`.
The German translation is in `i18n/de.po`.
