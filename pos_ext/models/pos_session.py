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
        currency_mxn = self.env['res.currency'].browse(self.env.ref('base.USD').id)
        for product in products:
            variants = variants.filtered(lambda var: var.min_weight <= product['weight'] <= var.max_weight)
            if variants:
                fixed_price = self.env['ir.config_parameter'].sudo().get_param('stock_ext.retail_variant_amount')
                price = (float(fixed_price) * product['weight']) * variants[0].value
                price = price - (price * 15/100)
                product['lst_price'] = price * currency_mxn.inverse_rate
