# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _default_sellers(self):
        sellers = self.env['res.partner'].search([('company_id', '=', self.env.company.id), ('user_ids', '!=', False)])
        return sellers

    payment_seller_ids = fields.Many2many('res.partner', string='Payment Sellers',
                                          default=lambda self: self._default_sellers())
