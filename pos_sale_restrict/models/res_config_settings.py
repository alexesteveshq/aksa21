# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fixed_commission_percentage = fields.Float(related='pos_config_id.fixed_commission_percentage', readonly=False)
