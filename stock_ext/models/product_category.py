# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductCategory, self).create(vals_list)
        expense_acc = self.env['account.account'].search([('code', '=', '601.84.02')])
        for categ in res:
            categ.write({'property_valuation': 'real_time',
                         'property_account_expense_categ_id': expense_acc.id})
        return res
