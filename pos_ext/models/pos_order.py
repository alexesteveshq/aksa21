# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


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

    def update_pos(self, company_id=False, backup_company_id=False, store_name=False):
        journal_model = self.env['account.journal']
        company = self.env['res.company'].browse(company_id)
        pos_payment_method = self.env['pos.payment.method']
        acc_model = self.env['account.account']
        config_model = self.env['pos.config']
        move_model = self.env['account.move']
        journals = journal_model.search([('company_id', '=', company.id),
                                         ('code', 'in', ['CSH1', 'BNK1', 'POS'])])
        if 'POS' not in journals.mapped('code'):
            journals |= self.env['account.journal'].create({'name': _('Point of sale'),
                                                            'type': 'general',
                                                            'code': 'POS',
                                                            'company_id': company.id})
        methods = pos_payment_method.search([('journal_id.code', 'in', ['CSH1', 'BNK1']),
                                             ('company_id', '=', company.id)])
        if not methods:
            methods |= pos_payment_method.create([
                {'name': _('Cash'),
                 'journal_id': journals.filtered(lambda jn: jn.code == 'CSH1').id,
                 'company_id': company.id},
                {'name': _('Bank'),
                 'journal_id': journals.filtered(lambda jn: jn.code == 'BNK1').id,
                 'company_id': company.id}])
        pos_config = config_model.search([('company_id', '=', company.id)])
        if not pos_config:
            pos_config = config_model.create(
                {'name': company.name,
                 'invoice_journal_id': journals.filtered(lambda jn: jn.code == 'POS').id,
                 'company_id': company.id,
                 'payment_method_ids': methods.ids})
        pos_orders = self.env['pos.order'].search([('name', 'ilike', store_name)])
        pos_orders.write({'company_id': company.id})
        for payment in pos_orders.mapped('payment_ids'):
            payment.session_id.write({'company_id': company.id, 'config_id': pos_config.id})
            payment.payment_method_id = methods.filtered(
                lambda me: me.journal_id.code == payment.payment_method_id.journal_id.code)
        assets = move_model.search([('journal_id.code', '!=', 'INV'),
                                    ('company_id', '=', backup_company_id),
                                    ('id', 'in', pos_orders.mapped('session_move_id').ids)])
        accounts = acc_model.search([('company_id', '=', company_id),
                                     ('code', 'in', ['102.01.02', '101.01.01', '401.01.01',
                                                     '105.01.02', '102.01.04', '9992', '9991'])])
        for asset in assets:
            if asset.journal_id.code in journals.mapped('code'):
                journal = journals.filtered(lambda jn: jn.code == asset.journal_id.code)
                move = move_model.create({
                    'company_id': company.id,
                    'journal_id': journal.id,
                    'date': asset.date,
                    'move_type': asset.move_type,
                    'line_ids': [(0, 0, {'account_id': accounts.filtered(
                        lambda acc: acc.code == line.account_id.code).id,
                                         'debit': line.debit,
                                         'credit': line.credit}) for line in asset.line_ids]})
                pos_orders.filtered(lambda order: order.session_move_id == asset).write(
                    {'session_move_id': move.id})


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        result = super(ReportSaleDetails, self.with_context(no_convert=True)).get_sale_details(
            date_start, date_stop, config_ids, session_ids)
        return result
