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
    cost_3 = fields.Float(string='Cost 3', compute='_compute_cost_3', store=True)
    price_usd = fields.Float(string='Price USD', compute='_compute_price', store=True, readonly=False)
    price_mxn = fields.Float(string='Price MXN', compute='_compute_price', store=True, readonly=False)
    print_enabled = fields.Boolean(string='Print enabled')

    @api.depends('lot_id', 'lot_id.cost_2', 'lot_id.additional_usd', 'weight')
    def _compute_cost_3(self):
        for piece in self:
            piece.cost_3 = (piece.lot_id.cost_2 + piece.lot_id.additional_usd) * piece.weight

    @api.depends('lot_id', 'cost_3', 'lot_id.tax_id', 'lot_id.variant')
    def _compute_price(self):
        currency_model = self.env['res.currency']
        for piece in self:
            price_untaxed = (piece.cost_3 * (piece.lot_id.variant or 1))
            price = price_untaxed + (price_untaxed * piece.lot_id.tax_id.amount/100)
            currency_usd = currency_model.browse(self.env.ref('base.USD').id)
            currency_mxn = currency_model.browse(self.env.ref('base.MXN').id)
            price_mxn = currency_usd._convert(int(price), currency_mxn, self.env.company, fields.Date.today())
            piece.price_usd = piece.lot_id.purchase_cost if not price else price
            piece.price_mxn = piece.lot_id.purchase_cost if not price else price_mxn

    def print_sticker(self):
        manager = LabelManager()
        data = {'code': self.barcode or "",
                'product': self.product_id.name or "",
                'weight': self.weight,
                'price_usd': str(int(self.price_usd)),
                'price_mxn': str(int(self.price_mxn))}
        label = manager.generate_label_data(data)
        self.write({'raw_data': label.dumpZPL(), 'print_enabled': True})
