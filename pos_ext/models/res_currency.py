# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _convert(self, from_amount, to_currency, company, date, round=True):
        result = super(ResCurrency, self)._convert(from_amount, to_currency, company, date, round)
        if self._context.get('no_convert'):
            return from_amount
        return result
