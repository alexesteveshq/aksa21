# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_payment_seller_ids = fields.Many2many(related='pos_config_id.payment_seller_ids', readonly=False)
