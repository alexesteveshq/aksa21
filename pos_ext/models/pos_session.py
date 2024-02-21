# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].extend(['weight', 'retail_price_untaxed'])
        return result

    def get_pos_ui_product_product_by_params(self, custom_search_params):
        products = super(PosSession, self).get_pos_ui_product_product_by_params(custom_search_params)
        for product in products:
            if product['retail_price_untaxed']:
                product['lst_price'] = product['retail_price_untaxed']
        return products

    def find_product_by_barcode(self, barcode):
        result = super(PosSession, self).find_product_by_barcode(barcode)
        if 'product_id' not in result:
            product = self.env['product.product'].search([
                ('barcode', '=', barcode),
                ('sale_ok', '=', True),
            ])
            if product:
                return {'product_id': [product.id]}
        return result

    def _prepare_line(self, order_line):
        res = super(PosSession, self)._prepare_line(order_line)
        exch_rate = self.env['res.currency.rate'].search([
            ('name', '=', order_line.order_id.date_order.date()),
            ('currency_id.name', '=', 'USC')])
        if exch_rate and order_line.currency_id.name != 'MXR':
            res['amount'] = (res['amount'] / 18) * exch_rate.inverse_company_rate
            if 'taxes' in res and res['taxes']:
                res['taxes'][0]['amount'] = (res['taxes'][0]['amount'] / 18) * exch_rate.inverse_company_rate
        return res

    def _create_non_reconciliable_move_lines(self, data):
        tax_account = self.env['account.account'].search(
            [('code', '=', '210.01.01'), ('company_id', '=', self.env.company.id)])
        if not self.picking_ids or not tax_account:
            return super(PosSession, self)._create_non_reconciliable_move_lines(data)
        taxes = data.get('taxes')
        sales = data.get('sales')
        stock_expense = data.get('stock_expense')
        MoveLine = data.get('MoveLine')
        tax_vals = [self._get_tax_vals(key, amounts['amount'], amounts['amount_converted'], amounts['base_amount_converted']) for key, amounts in taxes.items()]
        sale_vals = [self._get_sale_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in sales.items()]
        # Check if all taxes lines have account_id assigned. If not, there are repartition lines of the tax that have no account_id.
        tax_names_no_account = [line['name'] for line in tax_vals if line['account_id'] == False]
        if len(tax_names_no_account) > 0:
            error_message = _(
                'Unable to close and validate the session.\n'
                'Please set corresponding tax account in each repartition line of the following taxes: \n%s'
            ) % ', '.join(tax_names_no_account)
            raise UserError(error_message)
        MoveLine.create(tax_vals)
        move_line_ids = MoveLine.create(sale_vals)
        for key, ml_id in zip(sales.keys(), move_line_ids.ids):
            sales[key]['move_line_id'] = ml_id
        for key, amounts in stock_expense.items():
            untaxed_amount = amounts['amount'] / 1.16
            tax_amount = (untaxed_amount * self.env.company.account_sale_tax_id.amount) / 100
            MoveLine.create(self._get_stock_expense_vals(key, untaxed_amount, untaxed_amount))
            MoveLine.create(self._get_stock_expense_vals(tax_account, tax_amount, tax_amount))
        return data
