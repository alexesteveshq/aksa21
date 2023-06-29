# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].extend(['weight', 'retail_variant'])
        return result

    def get_pos_ui_product_product_by_params(self, custom_search_params):
        products = super(PosSession, self).get_pos_ui_product_product_by_params(custom_search_params)
        variants = self.env['piece.variant'].search([])
        currency_mxn = self.env['res.currency'].browse(self.env.ref('base.USD').id)
        for product in products:
            variant = variants.filtered(lambda var: var.min_weight <= product['weight'] <= var.max_weight)
            if variant:
                price = (float(product['retail_variant']) * product['weight']) * variant.value
                price = price - (price * 15 / 100)
                product['lst_price'] = price * currency_mxn.inverse_rate
        return products
