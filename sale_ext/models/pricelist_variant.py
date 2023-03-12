# -*- coding: utf-8 -*-

from odoo import fields, models


class PricelistVariant(models.Model):
    _name = 'pricelist.variant'
    _description = 'Pricelist Variant'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    min_weight = fields.Float(string='Min weight')
    max_weight = fields.Float(string='Max weight')
    value = fields.Float(string='Value')
