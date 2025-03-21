# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    fixed_commission_percentage = fields.Float(string='Fixed commission percentage')
