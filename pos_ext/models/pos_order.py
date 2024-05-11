# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    product_category_id = fields.Many2one(related='product_id.categ_id', store=True, index=True)
    amount_currency = fields.Float(string='Amount currency')

    @api.model_create_multi
    def create(self, vals_list):
        result = super(PosOrderLine, self).create(vals_list)
        currency_mxr = self.env['res.currency'].search([('name', '=', 'MXR')])
        for line in result:
            converted_amount = line.order_id.pricelist_id.currency_id._convert(
                line.price_subtotal_incl, currency_mxr, line.order_id.company_id, fields.Date.today())
            line.amount_currency = converted_amount
        return result


class PosOrder(models.Model):
    _inherit = 'pos.order'

    amount_currency = fields.Float(string='Amount currency')
    sale_qty = fields.Integer(string='Sale qty', compute='_compute_sale_qty', store=True)
    bank_paid_amount = fields.Float(string='Bank paid amount', compute='_payment_method_paid', store=True)
    cash_paid_amount = fields.Float(string='Cash paid amount', compute='_payment_method_paid', store=True)
    date_order = fields.Datetime(readonly=False)
    lines = fields.One2many(readonly=False)
    payment_ids = fields.One2many(readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        result = super(PosOrder, self).create(vals_list)
        currency_mxr = self.env['res.currency'].search([('name', '=', 'MXR')])
        for order in result:
            converted_amount = order.pricelist_id.currency_id._convert(
                order.amount_total, currency_mxr, order.company_id, fields.Date.today())
            order.amount_currency = converted_amount
        return result

    @api.depends('payment_ids', 'payment_ids.amount')
    def _payment_method_paid(self):
        for order in self:
            order.bank_paid_amount = sum(order.mapped('payment_ids').filtered(
                lambda pay: pay.payment_method_id.journal_id.code == 'BNK1').mapped('amount'))
            order.cash_paid_amount = sum(order.mapped('payment_ids').filtered(
                lambda pay: pay.payment_method_id.journal_id.code == 'CSH1').mapped('amount'))

    @api.depends('lines', 'lines.qty')
    def _compute_sale_qty(self):
        for order in self:
            order.sale_qty = abs(sum(order.mapped('lines.qty')))

    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)
        if 'seller_id' in ui_order:
            result['seller_id'] = ui_order['seller_id']
        return result


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        result = super(ReportSaleDetails, self.with_context(no_convert=True)).get_sale_details(
            date_start, date_stop, config_ids, session_ids)
        lines = self.env['pos.order'].search(
            ['|', ('session_id', 'in', session_ids or []),
             '&', ('date_order', '>=', date_start),
             ('date_order', '<=', date_stop)]).mapped('lines').sorted('order_id')
        order_payments = self.env["pos.payment"].search(
            [('pos_order_id', 'in', lines.mapped('order_id').ids)])
        payments, products = [], []
        for line in lines:
            values = {'date': line.order_id.date_order,
                      'partner': line.order_id.partner_id.name or "",
                      'cashier': line.order_id.seller_id.name or "",
                      'code': line.product_id.code,
                      'discount': line.discount,
                      'price_unit': round(line.price_subtotal, 2),
                      'product_id': line.product_id.id,
                      'product_name': line.product_id.display_name,
                      'quantity': line.qty,
                      'uom': line.product_uom_id.name}
            products.append(values)
        for method in order_payments.mapped('payment_method_id'):
            mth_payments = order_payments.filtered(lambda mth: mth.payment_method_id == method)
            payments.append({'name': method.name, 'total': round(sum(mth_payments.mapped('amount')), 2)})
        amount_total = round(sum(lines.mapped('amount_currency')), 2)
        amount_untaxed = amount_total / 1.16
        result.update({'products': products, 'payments': payments,
                       'total_paid': amount_total,
                       'taxes': [{'base_amount': amount_untaxed,
                                  'name': 'IVA 16% VENTAS',
                                  'tax_amount': amount_total - amount_untaxed}]})
        return result
