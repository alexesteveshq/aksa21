# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def seller_pos_assign(self):
        for partner in self:
            self.env['pos.config'].search([]).payment_seller_ids = [(4, partner.id)]
