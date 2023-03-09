# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(default='product')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    list_price = fields.Float(string='List price')
