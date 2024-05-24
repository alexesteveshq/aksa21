# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    quantity_average = fields.Float(string='Quantity average')
    discount_average = fields.Float(string='Discount average', readonly=True, group_operator="avg")
    sale_avg = fields.Float(string='Sale average', group_operator="avg")
    price_total_currency = fields.Float(string='Price total currency')
    seller_id = fields.Many2one('res.partner', string='Seller')

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(PosOrderReport, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)
        for value in result:
            if ('quantity_average' in value and 'order_id' in value and
                    isinstance(value['order_id'], int) and value['quantity_average']):
                value['quantity_average'] = round(value['quantity_average'] / value['order_id'], 2)
            if 'discount_average' in value and value['discount_average']:
                value['discount_average'] = round(value['discount_average'], 2)
            if 'sale_avg' in value and value['sale_avg']:
                value['sale_avg'] = round(value['sale_avg'], 2)
        return result

    def _select(self):
        result = super(PosOrderReport, self)._select()
        result += """, SUM(l.qty) AS quantity_average,
                AVG(l.discount) FILTER (WHERE l.discount > 0) AS discount_average,
                SUM(l.amount_currency) AS price_total_currency,
                SUM(l.price_subtotal_incl) AS sale_avg"""
        return result

    def _from(self):
        res = super(PosOrderReport, self)._from()
        res += """ WHERE l.qty != 0 """
        return res
