# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_usd = fields.Float(string='Sale Price')
    detailed_type = fields.Selection(default='product')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    price_usd = fields.Float(string='Sale Price')
    list_price = fields.Float(string='List price')
