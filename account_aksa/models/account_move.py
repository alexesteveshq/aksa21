# -*- coding: utf-8 -*-

from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def set_draft(self):
        for move in self:
            move.button_draft()
