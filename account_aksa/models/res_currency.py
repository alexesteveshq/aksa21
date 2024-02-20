# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def update_currency(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Update rates'),
            'res_model': 'currency.update.rate',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
            'views': [[False, 'form']]
        }

