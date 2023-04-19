# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def print_sticker_retail(self):
        piece_model = self.env['stock.piece']
        for quant in self:
            piece = piece_model.search([('barcode', '=', quant.product_id.barcode)])
            piece.print_sticker(retail=True)
