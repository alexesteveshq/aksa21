# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    seller_id = fields.Many2one('res.partner', string='Seller')
    commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission_amount', store=True)

    @api.depends('payment_ids', 'payment_ids.payment_method_id', 'payment_ids.amount',
                 'lines.product_id', 'lines.product_id.category_id',
                 'lines.price_subtotal', 'lines.price_subtotal_incl',
                 'seller_id', 'seller_id.is_admin', 'seller_id.admin_commission_rate',
                 'seller_id.commission_rate_ids', 'seller_id.commission_rate_ids.rate',
                 'seller_id.commission_rate_ids.payment_method_id',
                 'seller_id.category_commission_rate_ids',
                 'seller_id.category_commission_rate_ids.rate',
                 'seller_id.category_commission_rate_ids.category_id')
    def _compute_commission_amount(self):
        for order in self:
            order.commission_amount = 0
            if not order.amount_total or not order.seller_id:
                continue
            company_currency = order.company_id.currency_id
            total_with_tax_lines = sum(line.price_subtotal_incl for line in order.lines)
            untaxed_total_lines = sum(line.price_subtotal for line in order.lines)
            untaxed_ratio = untaxed_total_lines / total_with_tax_lines if total_with_tax_lines else 1.0

            total_in_company_currency = sum(
                (payment.payment_method_id.currency_id or company_currency)._convert(
                    payment.amount, company_currency, order.company_id, fields.Date.today())
                for payment in order.payment_ids
            ) * untaxed_ratio

            if order.seller_id.is_admin and order.seller_id.admin_commission_rate:
                order.commission_amount = (total_in_company_currency * order.seller_id.admin_commission_rate) / 100
                continue

            seller_categories = order.seller_id.category_commission_rate_ids
            matched_category = seller_categories.filtered(
                lambda c: any(line.product_id.category_id == c.category_id for line in order.lines))
            if matched_category:
                order.commission_amount = (total_in_company_currency * matched_category[0].rate) / 100
            else:
                for payment in order.payment_ids:
                    from_currency = payment.payment_method_id.currency_id or company_currency
                    amount = from_currency._convert(
                        payment.amount, company_currency, order.company_id, fields.Date.today()) * untaxed_ratio
                    commission_rate = order.seller_id.commission_rate_ids.filtered(
                        lambda r: r.payment_method_id == payment.payment_method_id)
                    if commission_rate.rate:
                        order.commission_amount += (amount * commission_rate.rate) / 100

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result['seller_name'] = order.seller_id.name
        return result
