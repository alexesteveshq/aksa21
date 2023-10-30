# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    retail_variant = fields.Float(string='Retail variant')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if res and self.retail_variant:
            for line in self.move_ids_without_package:
                line.product_id.retail_variant = self.retail_variant
