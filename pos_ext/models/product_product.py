# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if args and 'barcode' in args[0]:
            args[0] = ['barcode', 'ilike', args[0][2]]
        return super(ProductProduct, self).search(args, offset=offset, limit=limit, order=order, count=count)
