# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import ValidationError


class StockLot(models.Model):
    _inherit = 'stock.lot'

    weight_price = fields.Float(string='Price')
    product_qty = fields.Float(store=True)
    pieces_ids = fields.One2many('stock.piece', 'lot_id', string='Pieces')
    scale_read = fields.Boolean(string='Scale read')

    def calculate_lot_price(self):
        if self.scale_read:
            self.scale_read = False
        else:
            self.scale_read = True
