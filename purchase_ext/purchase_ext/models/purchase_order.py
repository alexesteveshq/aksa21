# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def set_costs(self):
        for order in self:
            for line in order.order_line:
                line.product_id.standard_price = line.price_unit
