# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from functools import partial

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class currency(models.Model):
    _inherit = 'res.currency'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    converted_currency = fields.Float('Currency', compute="_onchange_currency")

    @api.depends('company_id')
    def _onchange_currency(self):
        res_currency = self.env['res.currency'].search([])
        company_currency = self.env.user.company_id.currency_id
        for i in self:
            if i.id == company_currency.id:
                i.converted_currency = 1
            else:
                rate = (round(i.rate,6) / company_currency.rate)
                i.converted_currency = rate


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    converted_currency = fields.Float('Currency',related='currency_id.converted_currency')


class PosPayment(models.Model):
    _inherit = "pos.payment"

    amount_currency = fields.Float(string="Currency Amount")
    currency = fields.Many2one("res.currency", string="Currency")

class PosPaymentMethod(models.Model):

    _inherit = "pos.payment.method"

    currency_id = fields.Many2one("res.currency", 'Currency',compute='_compute_currency')

    def _compute_currency(self):
        for pm in self:
            pm.currency_id = pm.company_id.currency_id.id
            if pm.journal_id and pm.journal_id.currency_id:
                pm.currency_id = pm.journal_id.currency_id.id


class POSSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.extend(['product.pricelist.item'])
        return result

    def _loader_params_product_pricelist_item(self):
        return {
            'search_params': {
                'domain': [('pricelist_id', 'in', self.config_id.available_pricelist_ids.ids)],
                'fields': [],
            }
        }

    def _get_pos_ui_product_pricelist_item(self, params):
        return self.env['product.pricelist.item'].search_read(**params['search_params'])


    def load_pos_data(self):
        loaded_data = {}
        self = self.with_context(loaded_data=loaded_data)
        for model in self._pos_ui_models_to_load():
            loaded_data[model] = self._load_model(model)
        self._pos_data_process(loaded_data)        
        users_data = self._get_pos_ui_pos_res_currency(self._loader_params_pos_res_currency())
        loaded_data['currencies'] = users_data
        return loaded_data

    def _loader_params_pos_res_currency(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['name','symbol','position','rounding','rate','decimal_places','converted_currency'],
            },
        }

    def _get_pos_ui_pos_res_currency(self, params):
        currencies = self.env['res.currency'].search_read(**params['search_params'])
        return currencies


    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('currency_id')
        return result

    def _loader_params_product_pricelist(self):
        result = super()._loader_params_product_pricelist()
        result['search_params']['fields'].extend(['currency_id','converted_currency'])
        return result


class POSOrder(models.Model):

    _inherit = "pos.order"

    amount_total = fields.Float(string='Total', digits=0, required=True)
    amount_paid = fields.Float(string='Paid', digits=0, required=True)

    def _is_pos_order_paid(self):
        if (abs(self.amount_total - self.amount_paid) < 0.02):
            self.write({'amount_total': self.amount_paid})
            return True
        else:
            return False

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        payment_total = []
        company_id = self.env.user.company_id
        payment_date = ui_paymentline['name']
        payment_date = fields.Date.context_today(self, fields.Datetime.from_string(payment_date))
        price_unit_foreign_curr = 0.0

        price_unit_comp_curr = ui_paymentline['amount'] or 0.0
        currency_id = False

        if order.pricelist_id.currency_id.id != order.currency_id.id:
            # Convert
            price_unit_foreign_curr = ui_paymentline['amount']
            price_unit_comp_curr = order.pricelist_id.currency_id._convert(price_unit_foreign_curr, order.currency_id, order.company_id, payment_date)
            currency_id = order.pricelist_id.currency_id.id
            price_unit_comp_curr = price_unit_comp_curr

        return {
            'amount_currency': price_unit_foreign_curr,
            'currency': currency_id,
            'amount': price_unit_foreign_curr or price_unit_comp_curr,
            'payment_date': ui_paymentline['name'],
            'payment_method_id': ui_paymentline['payment_method_id'],
            'card_type': ui_paymentline.get('card_type'),
            'cardholder_name': ui_paymentline.get('cardholder_name'),
            'transaction_id': ui_paymentline.get('transaction_id'),
            'payment_status': ui_paymentline.get('payment_status'),
            'pos_order_id': order.id,
        }

    @api.model
    def _order_fields(self, ui_order):
        amount_total = []
        amt_total = ui_order['amount_total']
        amt_paid = ui_order['amount_paid']
        process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
        return {
            'user_id':      ui_order['user_id'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference': ui_order['name'],
            'sequence_number': ui_order['sequence_number'],
            'partner_id':   ui_order['partner_id'] or False,
            'date_order':   ui_order['creation_date'].replace('T', ' ')[:19],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'pricelist_id': ui_order['pricelist_id'],
            'amount_paid':  amt_paid,
            'amount_total':  amt_total,
            'amount_tax':  ui_order['amount_tax'],
            'amount_return':  ui_order['amount_return'],
            'company_id': self.env['pos.session'].browse(ui_order['pos_session_id']).company_id.id,
            'to_invoice': ui_order['to_invoice'] if "to_invoice" in ui_order else False,
            'is_tipped': ui_order.get('is_tipped', False),
            'tip_amount': ui_order.get('tip_amount', 0),
        }


class POSConfig(models.Model):
    
    _inherit = 'pos.config'
        
    @api.constrains('pricelist_id', 'use_pricelist', 'available_pricelist_ids', 'journal_id', 'invoice_journal_id', 'payment_method_ids')
    def _check_currencies(self):
        for config in self:
            if config.use_pricelist and config.pricelist_id not in config.available_pricelist_ids:
                raise ValidationError(_("The default pricelist must be included in the available pricelists."))

        if self.invoice_journal_id.currency_id and self.invoice_journal_id.currency_id != self.currency_id:
            raise ValidationError(_("The invoice journal must be in the same currency as the Sales Journal or the company currency if that is not set."))
