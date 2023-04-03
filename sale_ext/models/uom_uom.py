# -*- coding: utf-8 -*-

from odoo import fields, models


class UoM(models.Model):
    _inherit = 'uom.uom'

    def _compute_price(self, price, to_unit):
        if self._context.get('piece'):
            self._context.get('piece')._compute_price()
            price = self._context.get('piece').price_mxn_untaxed
        return super(UoM, self)._compute_price(price, to_unit)
