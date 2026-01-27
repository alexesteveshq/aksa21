# -*- coding: utf-8 -*-

from odoo import fields, models


class StockValuationUpdateWizard(models.Model):
    _name = 'stock.valuation.update.wizard'
    _description = 'Stock Valuation Update Wizard'

    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')
    category_id = fields.Many2one('stock.product.category', string='Category')
    value_increase = fields.Float(string='Value increase (%)')

    def update_stock(self):
        domain = [('create_date', '>=', self.date_start), ('create_date', '<=', self.date_end)]
        if self.category_id:
            domain.append(('category_code', '=', self.category_id.code))
        products = self.env['product.product'].with_context(active_test=False).sudo().search(domain)
        for product in products:
            self._cr.execute("""UPDATE product_product 
                                SET standard_price=standard_price + ((standard_price * %s) / 100) 
                                WHERE id=%s """, (self.value_increase, product.id))
