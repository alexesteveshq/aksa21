
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_registry = fields.Char(store=True)
