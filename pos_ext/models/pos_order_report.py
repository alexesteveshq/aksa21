# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    quantity_average = fields.Float(string='Quantity average', readonly=True, group_operator="avg")
    discount_average = fields.Float(string='Discount average', readonly=True, group_operator="avg")
    payment_method_id = fields.Many2one('pos.payment.method', string='Payment method', readonly=True)

    def _select(self):
        res = super(PosOrderReport, self)._select()
        res += (', s.line_qty AS quantity_average, SUM(l.discount) AS discount_average '
                ', pm.payment_method_id AS payment_method_id')
        return res

    def _from(self):
        res = super(PosOrderReport, self)._from()
        res += 'LEFT JOIN pos_payment pm ON (s.id = pm.pos_order_id)'
        return res

    def _group_by(self):
        res = super(PosOrderReport, self)._group_by()
        res += ',pm.payment_method_id'
        return res
