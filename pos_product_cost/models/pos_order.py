# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_cost = fields.Monetary(string='Total cost', compute='_compute_order_cost', store=True,
                                 currency_field='currency_id')

    @api.depends('lines', 'lines.total_cost')
    def _compute_order_cost(self):
        for order in self:
            order.order_cost = sum(order.mapped('lines.total_cost'))
