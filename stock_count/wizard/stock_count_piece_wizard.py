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

    @api.model
    def default_get(self, fields):
        result = super(StockCountPieceWizard, self).default_get(fields)
        result['missing_product_ids'] = self.env['stock.move'].search(
            [('company_id', '=', self.env.company.id)]).mapped('product_id')
        return result

    def on_barcode_scanned(self, barcode=''):
        if barcode:
            product = self.env['product.product'].search([('barcode', '=', barcode.upper())])
            if product:
                self.missing_product_ids = self.missing_product_ids.filtered(
                    lambda prod: prod.barcode != product.barcode)
                if self.missing_product_ids:
                    self.scan_status = 'missing_products'
                else:
                    self.scan_status = 'all_scanned'
        else:
            self.scan_status = 'not_detected'
