# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def post_closing_cash_details(self, counted_cash):
        draft_orders = self.order_ids.filtered(lambda order: order.state == 'draft')
        for order in draft_orders:
            difference = order.amount_total - order.amount_paid
            payment_method = order.session_id.payment_method_ids.sorted(lambda pm: pm.is_cash_count, reverse=True)[:1]
            if not float_is_zero(difference, precision_rounding=order.currency_id.rounding):
                order.add_payment({
                    'pos_order_id': order.id,
                    'amount': order._get_rounded_amount(difference),
                    'payment_method_id': payment_method.id,
                })
                if order._is_pos_order_paid():
                    order.action_pos_order_paid()
                    order._compute_total_cost_in_real_time()
        return super(PosSession, self).post_closing_cash_details(counted_cash)

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].extend(['weight', 'retail_price_untaxed_usd'])
        return result

    def get_pos_ui_product_product_by_params(self, custom_search_params):
        products = super(PosSession, self).get_pos_ui_product_product_by_params(custom_search_params)
        for product in products:
            if product['retail_price_untaxed_usd']:
                product['lst_price'] = product['retail_price_untaxed_usd']
        return products

    def _prepare_line(self, order_line):
        result = super(PosSession, self)._prepare_line(order_line)
        untaxed_amount = order_line.amount_currency / 1.16
        if 'amount' in result:
            result['amount'] = untaxed_amount
            result['amount_currency'] = untaxed_amount
        if 'taxes' in result and result['taxes']:
            result['taxes'][0]['amount'] = (order_line.amount_currency - untaxed_amount) * -1
            result['taxes'][0]['base'] = untaxed_amount * -1
        return result

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
