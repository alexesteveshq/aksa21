# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_system_diff = fields.Boolean(string='System difference')

    def action_balance_amounts(self):
        return {
            'name': _('Balance amounts'),
            'type': 'ir.actions.act_window',
            'res_model': 'balance.amounts.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
