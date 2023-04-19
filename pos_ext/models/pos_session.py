# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].append('weight')
        return result

    def _process_pos_ui_product_product(self, products):
        super(PosSession, self)._process_pos_ui_product_product(products)
        variants = self.env['piece.variant'].search([])
        for product in products:
            variants = variants.filtered(lambda var: var.min_weight <= product['weight'] <= var.max_weight)
            if variants:
                price = product['lst_price'] * variants[0].value
                product['lst_price'] = price - (price * 15/100)
