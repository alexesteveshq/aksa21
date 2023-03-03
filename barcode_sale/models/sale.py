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
        product = self.env['product.product'].search([('barcode', 'like', barcode)], limit=1)
        if product:
            self.order_line = [(0, 0, {'product_id': product.id,
                                       'product_uom_qty': 1,
                                       'price_unit': product.price_usd})]
        else:
            raise UserError(_('Scanned piece with barcode %s does not exist.') % barcode)
