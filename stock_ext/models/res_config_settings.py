# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    retail_variant_amount = fields.Float(string='Retail variant amount',
                                         config_parameter='stock_ext.retail_variant_amount')
    retail_usd_rate = fields.Float(string='Retail USD rate',
                                   config_parameter='stock_ext.retail_usd_rate')
