# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    commission_rate_ids = fields.One2many('commission.rate', 'partner_id', string='Commissions rates')
    category_commission_rate_ids = fields.One2many('category.commission.rate', 'partner_id', string='Category Commission Rates')
    is_admin = fields.Boolean(string='Is Admin')

    def seller_pos_assign(self):
        for partner in self:
            self.env['pos.config'].search([]).payment_seller_ids = [(4, partner.id)]
