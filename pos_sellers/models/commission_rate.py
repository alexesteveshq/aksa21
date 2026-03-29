# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class CommissionRate(models.Model):
    _name = 'commission.rate'

    payment_method_id = fields.Many2one('pos.payment.method', string='Payment Method')
    rate = fields.Float(string='Rate')
    partner_id = fields.Many2one('res.partner', string='Partner')
