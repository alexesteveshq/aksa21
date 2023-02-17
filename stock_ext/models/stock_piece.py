# -*- coding: utf-8 -*-

from odoo import fields, models
from ..LabelManager import LabelManager


class StockPiece(models.Model):
    _name = 'stock.piece'
    _description = 'Stock Piece'

    lot_id = fields.Many2one('stock.lot', string='Lot')
    product_id = fields.Many2one('product.product', string='Product')
    raw_data = fields.Char(string='Raw data')
    weight = fields.Float(string='Weight')
    price = fields.Float(string='Price')
    print_enabled = fields.Boolean(string='Print enabled')

    def print_sticker(self):
        manager = LabelManager()
        label = manager.generate_label_data(self.lot_id.name)
        self.write({'raw_data': label.code, 'print_enabled': True})
