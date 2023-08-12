# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    retail_variant = fields.Float(string='Retail variant')

    def purchase_transfered(self, location_id=False, company_id=False):
        quants = self.env['stock.quant'].search([('location_id', '=', location_id)])
        if quants and company_id:
            order = self.env['purchase.order'].create(
                {'name': 'Transfered products',
                 'company_id': company_id,
                 'partner_id': quants[0].company_id.partner_id.id,
                 'order_line': [(0, 0, {'product_id': quant.product_id.id, 'price_unit': 0})
                                for quant in quants]})
            order.button_confirm()

    @api.model_create_multi
    def create(self, vals):
        result = super(PurchaseOrder, self).create(vals)
        for purchase in result:
            purchase.mapped('order_line.product_id').filtered(lambda prod: not prod.retail_variant).write(
                {'retail_variant': purchase.retail_variant})
        return result

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if vals and 'retail_variant' in vals and vals['retail_variant']:
            for purchase in self:
                purchase.order_line.mapped('product_id').write({'retail_variant': purchase.retail_variant})
        return res
