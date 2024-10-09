# -*- coding: utf-8 -*-

from odoo import api, fields, models

import csv
import io
import base64


class StockCountPieceWizard(models.TransientModel):
    _name = 'stock.count.piece.wizard'
    _description = 'Count Piece Wizard'

    missing_product_count_ids = fields.Many2many('product.count', 'missing_count_piece_product_rel',
                                                 string='Missing Pieces')
    spare_product_count_ids = fields.Many2many('product.count', 'spare_count_piece_product_rel', string='Spare Pieces')
    date = fields.Date(default=fields.Date.today())
    barcodes = fields.Binary(string='Barcodes')
    scan_status = fields.Selection([('not_scanned', 'Not Scanned'),
                                    ('not_detected', 'Not Detected'),
                                    ('missing_products', 'Missing products'),
                                    ('all_scanned', 'All scanned'),
                                    ('error', 'Error')], string='Scan status', default='not_scanned')

    @api.model
    def default_get(self, fields):
        result = super(StockCountPieceWizard, self).default_get(fields)
        result['missing_product_count_ids'] = [
            (0, 0, {'product_id': product.id, 'quantity': product.qty_available})
            for product in self.env['product.product'].search([('qty_available', '>', 0)])]
        return result

    @api.onchange('barcodes')
    def _onchange_barcodes(self):
        if self.barcodes:
            self.process_barcodes()

    def print_pieces(self):
        self.process_barcodes()
        return {
            'type': 'ir.actions.report',
            'report_name': 'stock_count.report_stock_count_piece_wizard',
            'model': 'product.product',
            'report_type': 'qweb-pdf',
        }

    def process_barcodes(self):
        string_io = io.StringIO(base64.b64decode(self.barcodes).decode('utf-8'))
        csv_reader = csv.reader(string_io, delimiter=' ')
        codes = []
        try:
            for row in csv_reader:
                code = row[0].replace(',,', '').replace(',', '')
                codes.append(code)
            if codes:
                products = self.env['product.product'].with_context(count_pieces=True).search(
                    [('barcode', 'in', codes), ('qty_available', '>', 0)])
                not_found = [code for code in codes if code not in products.mapped('barcode')]
                not_found_prods = self.env['product.product'].with_context(count_pieces=True).search(
                    [('barcode', 'in', not_found)])
                if products:
                    for code in codes:
                        count_prod = self.missing_product_count_ids.filtered(lambda prod: prod.barcode == code)
                        if count_prod:
                            count_prod.quantity -= 1
                            if not count_prod.quantity:
                                self.missing_product_count_ids = self.missing_product_count_ids.filtered(
                                    lambda prod_count: prod_count.barcode != code)
                        else:
                            missing_prod = self.spare_product_count_ids.filtered(lambda prod: prod.barcode == code)
                            if missing_prod:
                                missing_prod.quantity += 1
                            else:
                                self.spare_product_count_ids = [(0, 0, {'product_id': not_found_prods.filtered(
                                    lambda prod: prod.barcode == code).id, 'quantity': 1})]
                    if self.missing_product_count_ids:
                        self.scan_status = 'missing_products'
                    else:
                        self.scan_status = 'all_scanned'
                else:
                    self.scan_status = 'not_detected'
        except Exception as e:
            self.scan_status = 'error'
