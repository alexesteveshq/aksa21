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
        for product in products:
            variant = self.config_id.pricelist_id.variant_ids.filtered(
                lambda var: var.min_weight <= product['weight'] <= var.max_weight)
            if variant:
                price = product['lst_price'] * variant.value
                product['lst_price'] = price - (price * 15/100)
