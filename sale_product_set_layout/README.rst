=======================
Sale Product Set Layout
=======================

Insert product sets (bills of materials) into quotations as a section, choose per
set how prices are printed and hide lines in reports.

**License:** AGPL-3 · **Author:** Biricon IT Services GmbH · **Odoo:** 19.0

Depends on ``sale_product_set`` (OCA/sale-workflow) and ``product_set``
(OCA/product-attribute).

Installation
============

The module needs two OCA addons from the **19.0** branches:

- ``sale_product_set`` from `OCA/sale-workflow <https://github.com/OCA/sale-workflow>`_
- ``product_set`` from `OCA/product-attribute <https://github.com/OCA/product-attribute>`_

Put these two modules and ``sale_product_set_layout`` into the addons path of your
instance, then update the apps list and install *Sale Product Set Layout*.

**Tip:** do not add the *complete* OCA repositories to the addons path of a
production system. Some modules in them are installed automatically as soon as
their dependencies are present (``auto_install``), for example
``purchase_product_template_tags`` in OCA/product-attribute. Link only the modules
you need into a separate directory and add that directory to the addons path.

Features
========

1. **Insert a product set as a section.** The wizard *Add set* creates a section
   named after the set (e.g. "2 × Measuring kit") and adds the set lines below it.
   Sections inside the set become subsections.
2. **Print mode per set** (adjustable in the wizard for each insertion):

   - *Print every line with its price*
   - *Print the lines without prices, set total only* (section "Hide Prices")
   - *Print only one line with the set total* (section "Hide Composition")

   The standard Odoo 19 section options are used, so the layout is passed on to
   the invoice and the customer portal.
3. **Hidden lines.** Set lines and order/invoice lines can be marked *Hidden*.
   They count for all totals (e.g. price corrections) but are neither printed nor
   shown in the portal. The flag is passed from the order line to the invoice line.
4. **Fixed price per set line**, e.g. for a hidden price correction.

Usage
=====

1. *Sales → Products → Product Sets*: create a set, choose *Insert as section* and
   the *Print mode*, add the lines. Mark correction lines as *Hidden* and give them
   a *Fixed price* if needed.
2. In a quotation click *Add set*, choose the set and the quantity.
3. Single order or invoice lines can be hidden with the column *Hidden in report*.

Hidden lines are part of the totals but invisible on the document. Check whether
this is compatible with the invoicing rules of your country.

Known issues / Roadmap
======================

- Hidden lines are part of the totals but invisible on the printed document and in
  the portal. They are still visible in the backend. Check whether this is
  compatible with the invoicing rules of your country before using it on invoices.
- The *Hidden* flag only affects the document layout. It does not change taxes,
  amounts or accounting entries.
- The module only changes how product sets are inserted and printed. Prices,
  discounts and taxes are still computed by standard Odoo.

Technical notes
===============

Extended models and added fields:

- ``product.set``: ``insert_as_section``, ``print_mode``
- ``product.set.line``: ``hide_in_report``, ``fixed_price``, ``price_unit``;
  ``prepare_sale_order_line_values()`` passes them to the order line
- ``sale.product.set.wizard``: ``insert_as_section``, ``section_name``,
  ``print_mode``; ``_prepare_order_lines()`` builds the section
- ``sale.order`` / ``sale.order.line``: ``hide_in_report``;
  ``_get_order_lines_to_report()`` skips hidden lines; ``_prepare_invoice_line()``
  passes the flag on
- ``account.move`` / ``account.move.line``: ``hide_in_report``;
  ``_get_move_lines_to_report()`` and the detailed/subsection line helpers skip
  hidden lines

The print mode is mapped to the standard section options ``collapse_prices``
(*total only*) and ``collapse_composition`` (*summary*). Sections inside a set are
inserted as subsections (``line_subsection``).

Run the tests with ``--test-enable --test-tags=/sale_product_set_layout``.
The German translation is in ``i18n/de.po``.

Credits
=======

Authors: Biricon IT Services GmbH
