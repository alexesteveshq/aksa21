# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    quantity_average = fields.Float(string='Quantity average')
    discount_average = fields.Float(string='Discount average', readonly=True, group_operator="avg")
    sale_avg = fields.Float(string='Sale average', group_operator="avg")
    cash_total = fields.Float(string='Cash total')
    bank_total = fields.Float(string='Bank total')
    sale_total = fields.Float(string='Sale total')

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(PosOrderReport, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)
        for value in result:
            if 'quantity_average' in value and 'order_id' in value and isinstance(value['order_id'], int):
                value['quantity_average'] = round(value['quantity_average'] / value['order_id'], 2)
            if 'discount_average' in value:
                value['discount_average'] = round(value['discount_average'], 2)
            if 'sale_avg' in value:
                value['sale_avg'] = round(value['sale_avg'], 2)
        return result

    def _select(self):
        res = super(PosOrderReport, self)._select()
        res += (', SUM(l.qty) AS quantity_average '
                ', AVG(l.discount) FILTER (WHERE l.discount > 0) AS discount_average '
                ', s.cash_paid_amount / s.sale_qty AS cash_total'
                ', s.bank_paid_amount / s.sale_qty AS bank_total'
                ', SUM(l.price_subtotal_incl) AS sale_total'
                ', SUM(l.price_subtotal_incl) AS sale_avg')
        return res

    def _from(self):
        res = super(PosOrderReport, self)._from()
        res += """ WHERE l.qty != 0 """
        return res
