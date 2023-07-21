# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    available_in_pos = fields.Boolean(string='Available in POS',
                                      compute='_compute_quantities', store=True)
    qty_available = fields.Float(store=True)

    @api.depends('stock_move_ids.product_qty', 'stock_move_ids.state')
    @api.depends_context(
        'lot_id', 'owner_id', 'package_id', 'from_date', 'to_date',
        'location', 'warehouse',
    )
    def _compute_quantities(self):
        super(ProductProduct, self)._compute_quantities()
        for product in self:
            if not product.qty_available:
                product.available_in_pos = False

    def write(self, vals):
        if vals and 'available_in_pos' in vals and vals['available_in_pos']:
            if not self.qty_available:
                vals['available_in_pos'] = False
        return super(ProductProduct, self).write(vals)
