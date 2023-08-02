# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    line_qty = fields.Integer(string='Line qty', compute='_compute_line_qty', store=True)

    @api.depends('lines')
    def _compute_line_qty(self):
        for order in self:
            order.line_qty = len(order.lines)
