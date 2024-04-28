# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    seller_id = fields.Many2one('res.partner', string='Seller')

    def _export_for_ui(self, order):
        result = super(PosOrder, self)._export_for_ui(order)
        result['seller_name'] = order.seller_id.name
        return result
