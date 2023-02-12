# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPiece(models.Model):
    _name = 'stock.piece'
    _description = 'Stock Piece'

    lot_id = fields.Many2one('stock.lot', string='Lot')
    product_id = fields.Many2one('product.product', string='Product')
    weight = fields.Float(string='Weight')
    price = fields.Float(string='Price')

    def create_from_scale(self, weight, lot_id):
        self.env['stock.piece'].create({'weight': weight, 'lot_id': lot_id})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def print_sticker(self):
        print("Hola")
