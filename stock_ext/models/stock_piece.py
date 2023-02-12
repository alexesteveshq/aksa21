# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPiece(models.Model):
    _name = 'stock.piece'
    _description = 'Stock Piece'

    lot_id = fields.Many2one('stock.lot', string='Lot')
    product_id = fields.Many2one('product.product', string='Product')
    weight = fields.Float(string='Weight')
    price = fields.Float(string='Price')
