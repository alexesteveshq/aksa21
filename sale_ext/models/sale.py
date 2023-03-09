# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_display_price(self):
        price = super(SaleOrderLine, self)._get_display_price()
        price = price * self.order_id.pricelist_id.variant
        return price
