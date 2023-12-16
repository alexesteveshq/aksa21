# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    payment_seller_ids = fields.Many2many('res.partner', related='config_id.payment_seller_ids',
                                          string='Payment Sellers')

    def load_pos_data(self):
        result = super(PosSession, self).load_pos_data()
        if self.payment_seller_ids:
            result['sellers'] = []
            for seller in self.payment_seller_ids:
                result['sellers'].append({'id': seller.id, 'name': seller.name})
        return result
