# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    quantity_average = fields.Float(string='Quantity average')
    discount_average = fields.Float(string='Discount average', readonly=True, group_operator="avg")
    sale_avg = fields.Float(string='Sale average', group_operator="avg")
    cash_total = fields.Float(string='Cash total')
    bank_total = fields.Float(string='Bank total')
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
        return """
            SELECT
                MIN(l.id) AS id,
                COUNT(*) AS nbr_lines,
                s.date_order AS date,
                SUM(l.qty) AS product_qty,
                SUM(l.qty * l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_sub_total,
                SUM((l.qty * l.price_unit) * (l.discount / 100) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS total_discount,
                CASE
                    WHEN SUM(l.qty * u.factor) = 0 THEN NULL
                    ELSE (SUM(l.qty*l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)/SUM(l.qty * u.factor))::decimal
                END AS average_price,
                SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                s.id as order_id,
                s.partner_id AS partner_id,
                s.state AS state,
                s.user_id AS user_id,
                s.company_id AS company_id,
                s.sale_journal AS journal_id,
                l.product_id AS product_id,
                pt.categ_id AS product_categ_id,
                p.product_tmpl_id,
                ps.config_id,
                s.seller_id AS seller_id,
                pt.pos_categ_id,
                s.pricelist_id,
                s.session_id,
                s.account_move IS NOT NULL AS invoiced,
                SUM(l.price_subtotal - COALESCE(l.total_cost,0) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS margin,
                SUM(l.qty) AS quantity_average,
                AVG(l.discount) FILTER (WHERE l.discount > 0) AS discount_average,
                s.cash_paid_amount / s.sale_qty AS cash_total,
                s.bank_paid_amount / s.sale_qty AS bank_total,
                SUM(l.price_subtotal_incl) AS price_total,
                SUM(l.price_subtotal_incl) AS sale_avg
        """

    def _from(self):
        res = super(PosOrderReport, self)._from()
        res += """ WHERE l.qty != 0 """
        return res
