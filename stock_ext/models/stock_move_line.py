# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def print_sticker_retail(self):
        piece_model = self.env['stock.piece']
        for move in self:
            piece = piece_model.search([('barcode', '=', move.product_id.barcode)])
            piece.print_sticker(retail=True)
