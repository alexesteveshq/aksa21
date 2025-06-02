
from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    expense_journal = fields.Boolean(string='Expense journal')
