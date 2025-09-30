# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    price_increase = fields.Float(string='Price increase')

    def print_stickers(self):
        purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
        for line in purchase_order.order_line:
            line.product_id.print_sticker()
