# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('import_file') and vals_list:
            prod_model = self.env['product.product']
            for val in vals_list:
                if 'order_line' in val:
                    for line in val['order_line']:
                        if 'product_qty' in line[2] and 'barcode' in line[2]:
                            product = prod_model.search([('barcode', '=', line[2]['barcode'])], limit=1)
                            if line[2]['product_qty'] > 1:
                                line[2]['price_unit'] *= 1.16
                            if not product:
                                product = prod_model.create({'name': line[2]['name'],
                                                              'standard_price': line[2]['price_unit']
                                                              if line[2]['product_qty'] > 1 else line[2]['price_unit'],
                                                              'barcode': line[2]['barcode'],
                                                              'weight': line[2]['weight']})
                            line[2]['product_id'] = product.id
        return super(PurchaseOrder, self).create(vals_list)

    def set_costs(self):
        for order in self:
            for line in order.order_line:
                line.product_id.standard_price = line.price_unit

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    barcode = fields.Char(string='barcode')
    weight = fields.Float(string='Weight')
