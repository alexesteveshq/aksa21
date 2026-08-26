# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    seller_id = fields.Many2one('res.partner', string='Seller')
    commission_amount = fields.Float(string='Commission Amount', compute='_compute_commission_amount', store=True)

    @api.depends('amount_total', 'payment_ids', 'payment_ids.payment_method_id', 'payment_ids.amount',
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

            total_with_tax_lines = sum(line.price_subtotal_incl for line in order.lines)
            untaxed_total_lines = sum(line.price_subtotal for line in order.lines)
            if not total_with_tax_lines:
                continue

            # Venta neta en la moneda de la compania: amount_total ya viene convertido con el
            # tipo de cambio que aplico el TPV en esa orden, no hace falta reconvertir los pagos.
            base = order.amount_total * (untaxed_total_lines / total_with_tax_lines)

            if order.seller_id.is_admin and order.seller_id.admin_commission_rate:
                order.commission_amount = (base * order.seller_id.admin_commission_rate) / 100
                continue

            commission = 0.0

            # Las lineas cuya categoria tiene tasa propia comisionan a esa tasa, solo por su parte.
            category_rates = {
                rate.category_id.id: rate.rate
                for rate in order.seller_id.category_commission_rate_ids
            }
            category_with_tax = 0.0
            for line in order.lines:
                rate = category_rates.get(line.product_id.category_id.id)
                if rate:
                    commission += (base * (line.price_subtotal_incl / total_with_tax_lines) * rate) / 100
                    category_with_tax += line.price_subtotal_incl

            # El resto se reparte entre los metodos de pago segun lo que aporto cada uno.
            remaining = 1 - (category_with_tax / total_with_tax_lines)
            total_paid = sum(order.payment_ids.mapped('amount'))
            if remaining > 0 and total_paid:
                for payment in order.payment_ids:
                    commission_rate = order.seller_id.commission_rate_ids.filtered(
                        lambda r: r.payment_method_id == payment.payment_method_id)
                    if commission_rate and commission_rate[0].rate:
                        commission += (base * remaining * (payment.amount / total_paid)
                                       * commission_rate[0].rate) / 100

            order.commission_amount = commission

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result['seller_name'] = order.seller_id.name
        return result
