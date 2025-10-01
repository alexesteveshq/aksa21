# -*- coding: utf-8 -*-
from odoo import fields, models, _


class UpdateProductPriceWizard(models.TransientModel):
    _name = 'update.product.price.wizard'
    _description = 'Update Product Price'

    price_increase = fields.Float(string='Price increase')

    def update_price(self):
        purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
        purchase_order.with_context(increase_price=True).mapped('order_line.product_id').update_price_percentage(
            self.price_increase)
        purchase_order._message_log(body=_('Prices updated by: %s percent' % self.price_increase))
        purchase_order.price_increase = self.price_increase
