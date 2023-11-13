# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def purchase_from_products(self):
        partner = self.env.ref('__custom__.aksa_partner')
        if self:
            self.env['purchase.order'].create(
                {'name': _('Aksa Products'), 'partner_id': partner.id, 'order_line':
                    [(0, 0, {'product_id': prod.id, 'price_unit': prod.standard_price}) for prod in self]})
