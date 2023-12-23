# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    seller_id = fields.Many2one('res.partner', string='Seller', readonly=True)

    def _select(self):
        return super(PosOrderReport, self)._select() + ',s.seller_id AS seller_id'
