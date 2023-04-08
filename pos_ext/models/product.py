# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    available_in_pos = fields.Boolean(string='Available in POS')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        for index, term in enumerate(args):
            if term[0] == 'barcode':
                args[index] = ['pieces_ids.barcode', 'in', [term[2]]]
        return super(ProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                   access_rights_uid=access_rights_uid)
