# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_unbalanced_moves(self, container):
        container['records'] = container['records'].filtered(lambda move: move.journal_id.code != 'POS')
        return super(AccountMove, self)._get_unbalanced_moves(container)
