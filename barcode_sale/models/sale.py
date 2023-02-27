# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import _, models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        piece = self.env['stock.piece'].search([('barcode', '=', barcode), ('product_id', '!=', False)], limit=1)
        order_lines = self.order_line.filtered(lambda r: r.piece_id == piece)
        if piece and not order_lines:
            self.order_line = [(0, 0, {'product_id': piece.product_id.id,
                                       'piece_id': piece.id,
                                       'product_uom_qty': 1,
                                       'price_unit': piece.price_usd})]
        else:
            raise UserError(_('Scanned barcode %s is not related to any piece or is not available.') % barcode)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    piece_id = fields.Many2one('stock.piece', string='Piece')
