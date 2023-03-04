# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    purchase_cost = fields.Float(string='Cost 1 (purchase)')
    acquisition_date = fields.Date(string='Acquisition date')
    import_cost = fields.Float(string='Import Cost %')
    variant = fields.Float(string='Variant')
    cost_2 = fields.Float(string='Cost 2 (logistic)', compute='_compute_cost_2', store=True, readonly=False)
    additional_usd = fields.Float(string='Additional USD')
    product_qty = fields.Float(store=True)
    pieces_ids = fields.One2many('stock.piece', 'lot_id', string='Pieces')
    scale_read = fields.Boolean(string='Scale read')
    tax_id = fields.Many2one('account.tax', string='Tax', default=lambda self: self.env.company.account_sale_tax_id)

    @api.depends('purchase_cost', 'import_cost')
    def _compute_cost_2(self):
        for lot in self:
            lot.cost_2 = lot.purchase_cost + (lot.purchase_cost * lot.import_cost/100)

    def calculate_lot_price(self):
        if self.scale_read:
            self.scale_read = False
        else:
            self.scale_read = True
