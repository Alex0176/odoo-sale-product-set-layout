This module extends the OCA module `sale_product_set` so that product sets can be
used as bills of materials in quotations, sales orders and invoices:

1. **Insert a product set as a section.** The wizard *Add set* creates a section
   named after the set (e.g. "2 × Measuring kit") and adds the set lines below it.
   Sections inside the set become subsections.
2. **Print mode per set** (can be changed in the wizard for each insertion):
   - *Print every line with its price*
   - *Print the lines without prices, set total only* (section "Hide Prices")
   - *Print only one line with the set total* (section "Hide Composition")

   The standard Odoo 19 section options are used, so the layout is passed on to
   the invoice and the customer portal.
3. **Hidden lines.** Set lines and order/invoice lines can be marked *Hidden*. They
   count for all totals (e.g. price corrections) but are not printed and not shown
   in the customer portal. The flag is passed from the order line to the invoice line.
4. **Fixed price per set line**, e.g. for a hidden price correction.
