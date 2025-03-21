# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    fixed_commission_percentage = fields.Float(related='config_id.fixed_commission_percentage',
                                               string='Fixed Commission Percentage')

    def load_pos_data(self):
        result = super(PosSession, self).load_pos_data()
        result['commission_percentage'] = 0
        if self.fixed_commission_percentage:
            result['commission_percentage'] = self.fixed_commission_percentage
        return result

    def _get_pos_ui_product_product(self, params):
        params['search_params']['fields'].append('category_code')
        return super(PosSession, self)._get_pos_ui_product_product(params)

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].extend(['category_code'])
        return result

    def _get_pos_ui_pos_payment_method(self, params):
        params['search_params']['fields'].append('commission_percentage_ids')
        result = super(PosSession, self)._get_pos_ui_pos_payment_method(params)
        for method in result:
            commission_percentages = self.env['commission.percentage'].browse(method['commission_percentage_ids'])
            percentages = [{'code': com.product_category_id.code, 'value': com.value} for com in commission_percentages]
            method['commission_percentage_ids'] = percentages
        return result
