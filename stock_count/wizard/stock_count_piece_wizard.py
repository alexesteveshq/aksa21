# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockCountPieceWizard(models.TransientModel):
    _name = 'stock.count.piece.wizard'
    _inherit = 'barcodes.barcode_events_mixin'
    _description = 'Count Piece Wizard'

    missing_product_ids = fields.Many2many('product.product', '', string='Missing Pieces')
    scan_status = fields.Selection([('not_scanned', 'Not Scanned'),
                                    ('not_detected', 'Not Detected'),
                                    ('missing_products', 'Missing products'),
                                    ('all_scanned', 'All scanned'),
                                    ('error', 'Error')], string='Scan status', default='not_scanned')
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')

    def on_barcode_scanned(self, barcode=''):
        self.missing_product_ids = False
        if barcode:
            stock_moves = self.env['stock.move'].search(
                [('location_id.usage', 'in', ('internal', 'transit')),
                 ('location_dest_id.usage', 'not in', ('internal', 'transit')),
                 ('date', '>=', self.start_date), ('date', '<=', self.end_date)])
            product_moves = stock_moves.mapped('product_id')
            try:
                barcodes = barcode.split('\n')
                barcodes = [value.upper() for value in barcodes]
                for barcode in barcodes:
                    product = self.env['product.product'].search([('barcode', '=', barcode)])
                    if product in product_moves:
                        product_moves -= product
                self.missing_product_ids = product_moves
                if self.missing_product_ids:
                    self.scan_status = 'missing_products'
                else:
                    self.scan_status = 'all_scanned'
            except Exception as e:
                self.scan_status = 'error'
        else:
            self.scan_status = 'not_detected'
