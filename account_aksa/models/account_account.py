# -*- coding: utf-8 -*-

from odoo import fields, models, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_type = fields.Selection(selection_add=[('expense_operative', 'Operative expense'),
                                                   ('expense_sale', 'Sale expense'),
                                                   ('expense_administrative', 'Administrative expense'),
                                                   ('expense_financial', 'Financial expense'),
                                                   ('expense_taxes_duties', 'Taxes and duties'),
                                                   ('expense_other_service', 'Other expenses and services')],
                                    ondelete={'expense_operative': 'cascade',
                                              'expense_sale': 'cascade',
                                              'expense_administrative': 'cascade',
                                              'expense_financial': 'cascade',
                                              'expense_taxes_duties': 'cascade',
                                              'expense_other_service': 'cascade'})

