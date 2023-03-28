# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    piece_id = fields.Many2one('stock.piece', string='Piece')

    def _get_display_price(self):
        price = super(SaleOrderLine, self.with_context(piece=self.piece_id))._get_display_price()
        variant = self.order_id.pricelist_id.variant_ids.filtered(
            lambda var: var.min_weight <= self.product_id.weight <= var.max_weight)
        if variant:
            price = price * variant.value
        return price
