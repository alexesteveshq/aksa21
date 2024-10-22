# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    import_qty = fields.Integer(string='Import Qty')

    def purchase_from_products(self):
        partner = self.env.ref('__custom__.aksa_partner')
        if self:
            self.env['purchase.order'].create( {'name': _('Aksa Products'), 'partner_id': partner.id,
                 'order_line': [(0, 0, {'product_id': prod.id, 'price_unit': prod.standard_price,
                                        'product_qty': prod.import_qty or 1}) for prod in self]})
