# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lot_discount_ids = fields.One2many('lot.discount', 'order_id', string='Lot discount')

    def set_line_pieces(self, lot_ids=[]):
        pieces = self.env['stock.piece'].search([('lot_id', 'in', lot_ids)])
        for order in self:
            for line in order.order_line:
                piece = line.piece_id
                if not piece:
                    piece = pieces.filtered(lambda p: p.product_id == line.product_id)
                    piece = piece if len(piece) <= 1 else piece[0]
                if piece:
                    line.write({'piece_id': piece, 'price_unit': piece.price_mxn_untaxed})
            discounts = {line.id: line.discount for line in order.order_line}
            order.action_update_prices()
            for line in order.order_line:
                line.discount = discounts[line.id]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    piece_id = fields.Many2one('stock.piece', string='Piece')
    piece_lot_it = fields.Many2one(related='piece_id.lot_id')
    barcode = fields.Char(related='piece_id.barcode')
    weight = fields.Float(related='piece_id.weight')
    discount = fields.Float()

    @api.onchange('piece_id')
    def onchange_piece_id(self):
        if self.piece_id:
            self.product_id = self.piece_id.product_id

    def _get_display_price(self):
        price = super(SaleOrderLine, self.with_context(piece=self.piece_id))._get_display_price()
        variant = self.order_id.pricelist_id.variant_ids.filtered(
            lambda var: var.min_weight <= self.product_id.weight <= var.max_weight)
        if variant:
            price = price * variant.value
        return price

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'order_id.lot_discount_ids',
                 'order_id.lot_discount_ids.lot_id', 'order_id.lot_discount_ids.value')
    def _compute_discount(self):
        super(SaleOrderLine, self)._compute_discount()
        for line in self:
            disc_line = line.order_id.lot_discount_ids.filtered(lambda disc: disc.lot_id == line.piece_id.lot_id)
            if disc_line:
                line.discount = disc_line[0].value
