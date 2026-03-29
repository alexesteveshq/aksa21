# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    seller_id = fields.Many2one('res.partner', string='Seller')
    commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission_amount', store=True)

    @api.depends('payment_ids', 'payment_ids.payment_method_id', 'payment_ids.amount',
                 'lines.product_id', 'lines.product_id.category_id',
                 'session_id.config_id.admin_commission_rate')
    def _compute_commission_amount(self):
        for order in self:
            order.commission_amount = 0
            company_currency = order.company_id.currency_id

            total_in_company_currency = sum(
                (payment.payment_method_id.currency_id or company_currency)._convert(
                    payment.amount, company_currency, order.company_id, fields.Date.today())
                for payment in order.payment_ids
            )

            if order.seller_id.is_admin:
                order.commission_amount = (total_in_company_currency * order.session_id.config_id.admin_commission_rate) / 100
            else:
                seller_categories = order.seller_id.category_commission_rate_ids
                matched_category = seller_categories.filtered(
                    lambda c: any(line.product_id.category_id == c.category_id for line in order.lines))
                if matched_category:
                    order.commission_amount = (total_in_company_currency * matched_category[0].rate) / 100
                else:
                    for payment in order.payment_ids:
                        from_currency = payment.payment_method_id.currency_id or company_currency
                        amount = from_currency._convert(
                            payment.amount, company_currency, order.company_id, fields.Date.today())
                        commission_rate = order.seller_id.commission_rate_ids.filtered(
                            lambda r: r.payment_method_id == payment.payment_method_id)
                        if commission_rate.rate:
                            order.commission_amount += (amount * commission_rate.rate) / 100

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result['seller_name'] = order.seller_id.name
        return result
