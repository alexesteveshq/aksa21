# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_display_price(self):
        price = super(SaleOrderLine, self)._get_display_price()
        variant = self.order_id.pricelist_id.variant_ids.filtered(
            lambda var: var.min_weight <= self.product_id.weight <= var.max_weight)
        if variant:
            price = price * variant.value
        return price
