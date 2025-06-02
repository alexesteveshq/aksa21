
from odoo import models, fields, api, _

class AccountAccount(models.Model):
    _inherit = 'account.account'

    legacy_report = fields.Boolean(string="Legacy Report")
