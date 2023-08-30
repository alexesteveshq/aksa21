# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].extend(['weight', 'retail_price_untaxed'])
        return result

    def get_pos_ui_product_product_by_params(self, custom_search_params):
        products = super(PosSession, self).get_pos_ui_product_product_by_params(custom_search_params)
        for product in products:
            if product['retail_price_untaxed']:
                product['lst_price'] = product['retail_price_untaxed']
        return products

    def find_product_by_barcode(self, barcode):
        result = super(PosSession, self).find_product_by_barcode(barcode)
        if 'product_id' not in result:
            product = self.env['product.product'].search([
                ('barcode', '=', barcode),
                ('sale_ok', '=', True),
            ])
            if product:
                return {'product_id': [product.id]}
        return result
