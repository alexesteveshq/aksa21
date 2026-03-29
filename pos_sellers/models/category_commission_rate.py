# -*- coding: utf-8 -*-

from odoo import fields, models


class CategoryCommissionRate(models.Model):
    _name = 'category.commission.rate'

    category_id = fields.Many2one('stock.product.category', string='Category', required=True)
    rate = fields.Float(string='Rate (%)')
    partner_id = fields.Many2one('res.partner', string='Partner')
