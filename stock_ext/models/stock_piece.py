# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ..LabelManager import LabelManager


class StockPiece(models.Model):
    _name = 'stock.piece'
    _description = 'Stock Piece'
    _rec_name = 'barcode'

    def _default_piece_barcode(self):
        return self.env['ir.sequence'].next_by_code('stock_ext.stock_piece')

    lot_id = fields.Many2one('stock.lot', string='Lot')
    barcode = fields.Char(string='Barcode', default=_default_piece_barcode)
    product_id = fields.Many2one('product.product', string='Product')
    raw_data = fields.Char(string='Raw data')
    weight = fields.Float(string='Weight')
    price_usd = fields.Float(string='Price USD', compute='_compute_price', store=True, readonly=False)
    price_mxn = fields.Float(string='Price MXN', compute='_compute_price', store=True, readonly=False)
    print_enabled = fields.Boolean(string='Print enabled')

    @api.depends('lot_id', 'lot_id.weight_price')
    def _compute_price(self):
        for piece in self:
            piece.price_usd = piece.lot_id.weight_price
            piece.price_mxn = piece.lot_id.weight_price

    def print_sticker(self):
        manager = LabelManager()
        data = {'code': self.barcode or "",
                'product': self.product_id.name or "",
                'weight': self.weight,
                'price_usd': str(int(self.price_usd)),
                'price_mxn': str(int(self.price_mxn))}
        label = manager.generate_label_data(data)
        self.write({'raw_data': label.dumpZPL(), 'print_enabled': True})
