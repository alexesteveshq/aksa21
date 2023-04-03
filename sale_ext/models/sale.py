# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lot_discount_ids = fields.One2many('lot.discount', 'order_id', string='Lot discount')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    piece_id = fields.Many2one('stock.piece', string='Piece')
    piece_lot_it = fields.Many2one(related='piece_id.lot_id')
    barcode = fields.Char(related='piece_id.barcode')
    weight = fields.Float(related='piece_id.weight')
    discount = fields.Float()

    def _get_display_price(self):
        price = super(SaleOrderLine, self.with_context(piece=self.piece_id))._get_display_price()
        variant = self.order_id.pricelist_id.variant_ids.filtered(
            lambda var: var.min_weight <= self.product_id.weight <= var.max_weight)
        if variant:
            price = price * variant.value
        return price
