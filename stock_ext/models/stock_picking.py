# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    retail_variant = fields.Float(string='Retail variant')

    @api.model_create_multi
    def create(self, vals):
        result = super(StockPicking, self).create(vals)
        for picking in result:
            picking.move_line_ids.mapped('product_id').write({'retail_variant': picking.retail_variant})
        return result

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if vals and 'retail_variant' in vals and vals['retail_variant']:
            for picking in self:
                picking.move_line_ids.mapped('product_id').write({'retail_variant': picking.retail_variant})
        return res
