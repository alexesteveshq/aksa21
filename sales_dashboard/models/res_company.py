
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_branch = fields.Boolean(string='Is branch')
