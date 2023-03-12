# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    variant_ids = fields.One2many('pricelist.variant', 'pricelist_id', string='Variants')
