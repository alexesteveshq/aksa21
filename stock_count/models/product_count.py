# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductCount(models.Model):
    _name = 'product.count'
    _description = 'Product Count'

    product_id = fields.Many2one('product.product', string='Product')
    barcode = fields.Char(related='product_id.barcode')
    name = fields.Char(related='product_id.name')
    standard_price = fields.Float(related='product_id.standard_price')
    quantity = fields.Integer(string='Quantity')
