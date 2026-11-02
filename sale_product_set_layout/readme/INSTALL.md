The module needs two OCA addons from the **19.0** branches:

- `sale_product_set` from [OCA/sale-workflow](https://github.com/OCA/sale-workflow)
- `product_set` from [OCA/product-attribute](https://github.com/OCA/product-attribute)

Put these two modules and `sale_product_set_layout` into the addons path of your
instance, then update the apps list and install *Sale Product Set Layout*.

**Tip:** do not add the *complete* OCA repositories to the addons path of a
production system. Some modules in them are installed automatically as soon as
their dependencies are present (`auto_install`), for example
`purchase_product_template_tags` in OCA/product-attribute. Link only the modules
you need into a separate directory and add that directory to the addons path.
