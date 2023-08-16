# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    quantity_average = fields.Float(string='Quantity average', readonly=True, group_operator="avg")
    discount_average = fields.Float(string='Discount average', readonly=True, group_operator="avg")
    sale_avg = fields.Float(string='Sale average', group_operator="avg")
    cash_total = fields.Float(string='Cash total')
    bank_total = fields.Float(string='Bank total')
    sale_total = fields.Float(string='Sale total')

    def _select(self):
        res = super(PosOrderReport, self)._select()
        res += (', s.sale_qty AS quantity_average, SUM(l.discount) AS discount_average '
                ', s.cash_paid_amount / s.sale_qty AS cash_total'
                ', s.bank_paid_amount / s.sale_qty AS bank_total'
                ', s.amount_paid / s.sale_qty AS sale_total'
                ', s.amount_paid AS sale_avg')
        return res