# -*- coding: utf-8 -*-

from odoo import fields, models


class PieceVariant(models.Model):
    _name = 'piece.variant'
    _description = 'Piece Variant'

    pricelist_id = fields.Many2one('piece.pricelist', string='Pricelist')
    min_weight = fields.Float(string='Min weight')
    max_weight = fields.Float(string='Max weight')
    value = fields.Float(string='Value')
