# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    total_cost = fields.Float(string='Total cost')

    def _select(self):
        result = super(PosOrderReport, self)._select()
        result += ", SUM(l.total_cost) AS total_cost"
        return result
