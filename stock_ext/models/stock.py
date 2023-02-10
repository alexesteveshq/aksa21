# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import ValidationError
from ..ScaleDriver import ScaleManager


class StockLot(models.Model):
    _inherit = 'stock.lot'

    weight_price = fields.Float(string='Price')
    product_qty = fields.Float(store=True)

    def calculate_lot_price(self):
        weight = ScaleManager.get_value()
        if not weight:
            raise ValidationError("Unable to calculate weight, please check the scale connection.")
        self.product_qty = float(weight)
        if self.product_id:
            self.weight_price = self.product_qty * self.product_id.standard_price
