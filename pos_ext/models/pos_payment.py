# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    amount = fields.Monetary(readonly=False)
    payment_method_id = fields.Many2one(readonly=False)
    currency_id = fields.Many2one(redonly=False)
