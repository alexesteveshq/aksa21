# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    product_category_id = fields.Many2one(related='product_id.categ_id', store=True, index=True)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    sale_qty = fields.Integer(string='Sale qty', compute='_compute_sale_qty', store=True)
    bank_paid_amount = fields.Float(string='Bank paid amount', compute='_payment_method_paid', store=True)
    cash_paid_amount = fields.Float(string='Cash paid amount', compute='_payment_method_paid', store=True)

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
        currency_mxr = self.env['res.currency'].search([('name', '=', 'MXR')])
        if 'lines' in result:
            for line in result['lines']:
                line[2]['price_unit'] = line[2]['price_unit'] * currency_mxr.rate
                line[2]['price_subtotal'] = line[2]['price_subtotal'] * currency_mxr.rate
                line[2]['price_subtotal_incl'] = line[2]['price_subtotal_incl'] * currency_mxr.rate
            result['amount_paid'] = result['amount_paid'] * currency_mxr.rate
            result['amount_total'] = result['amount_total'] * currency_mxr.rate
            result['amount_tax'] = result['amount_tax'] * currency_mxr.rate
        return result

    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        currency_mxr = self.env['res.currency'].search([('name', '=', 'MXR')])
        if 'statement_ids' in pos_order:
            for stmt in pos_order['statement_ids']:
                stmt[2]['amount'] = stmt[2]['amount'] * currency_mxr.rate
        super(PosOrder, self)._process_payment_lines(pos_order, order, pos_session, draft)


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        result = super(ReportSaleDetails, self.with_context(no_convert=True)).get_sale_details(
            date_start, date_stop, config_ids, session_ids)
        lines = self.env['pos.session'].browse(session_ids).mapped('order_ids.lines').sorted('order_id')
        order_payments = self.env["pos.payment"].search(
            [('pos_order_id', 'in', lines.mapped('order_id').ids)])
        payments, products = [], []
        for line in lines:
            values = {'date': line.order_id.date_order,
                      'partner': line.order_id.partner_id.name or "",
                      'cashier': line.order_id.cashier,
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
            if method.currency_id == self.env.company.currency_id:
                pay_total = sum(mth_payments.mapped('amount'))
            else:
                pay_total = sum(mth_payments.mapped('amount_currency'))
            payments.append({'name': method.name, 'total': round(pay_total, 2)})
        result.update({'products': products, 'payments': payments})
        return result
