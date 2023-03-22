# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ..LabelManager import LabelManager
import math


class StockPiece(models.Model):
    _name = 'stock.piece'
    _description = 'Stock Piece'
    _rec_name = 'barcode'

    def _default_piece_barcode(self):
        return self.env['ir.sequence'].next_by_code('stock_ext.stock_piece')

    lot_id = fields.Many2one('stock.lot', string='Lot')
    barcode = fields.Char(string='Barcode', default=_default_piece_barcode)
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    product_id = fields.Many2one('product.product', string='Product')
    raw_data = fields.Char(string='Raw data')
    weight = fields.Float(string='Weight')
    total_cost = fields.Float(string='Total Cost', compute='_compute_cost_3', store=True)
    cost_3 = fields.Float(string='Cost 3', compute='_compute_cost_3', store=True)
    price_usd = fields.Float(string='Price USD', compute='_compute_price', store=True, readonly=False)
    price_mxn = fields.Float(string='Price MXN', compute='_compute_price', store=True, readonly=False)
    print_enabled = fields.Boolean(string='Print enabled')

    def create_products(self):
        product_tmpl_model = self.env['product.template']
        products = self.env['product.product']
        currency_model = self.env['res.currency']
        for piece in self:
            if piece.product_tmpl_id:
                currency_mxn = currency_model.browse(self.env.ref('base.MXN').id)
                piece.price_mxn = piece.price_usd * currency_mxn.rate
                piece.product_id.write({'list_price': (piece.cost_3 * (piece.lot_id.variant or 1)),
                                        'standard_price': piece.cost_3,
                                        'weight': piece.weight})
                piece.print_sticker(False)
                piece.create_variant()
            else:
                products |= piece.product_id
                template = product_tmpl_model.search([('name', '=', piece.product_id.name),
                                                      ('detailed_type', '=', 'product')])
                if not template:
                    template = product_tmpl_model.create({'name': piece.product_id.name, 'detailed_type': 'product'})
                piece.product_tmpl_id = template
                piece.create_variant()
        products.unlink()

    def create_variant(self):
        product_model = self.env['product.product']
        weight_attr = self.env.ref('stock_ext.product_attribute_weight')
        value_model = self.env['product.attribute.value']
        if self.product_tmpl_id and not self.product_id:
            attr_value = value_model.search([('attribute_id', '=', weight_attr.id), ('name', '=', self.weight)])
            if attr_value:
                values = attr_value.ids
            else:
                values = [(0, 0, {'attribute_id': weight_attr.id, 'name': self.weight})]
            if not self.product_tmpl_id.attribute_line_ids:
                self.product_tmpl_id.attribute_line_ids = [
                    (0, 0, {'attribute_id': weight_attr.id, 'value_ids': values})]
            else:
                line = self.product_tmpl_id.attribute_line_ids.filtered(
                    lambda ln: ln.attribute_id == weight_attr)
                if attr_value:
                    line.value_ids = [(6, 0, line.value_ids.ids + values)]
                else:
                    line.value_ids = values
            variant = product_model.search([('product_template_variant_value_ids.name', '=', self.weight),
                                            ('detailed_type', '=', 'product'),
                                            ('product_tmpl_id', '=', self.product_tmpl_id.id)])
            self.barcode = variant.barcode if variant.barcode else self.barcode
            variant.write({'detailed_type': 'product',
                           'standard_price': self.cost_3,
                           'list_price': self.cost_3 * (self.lot_id.variant or 1),
                           'taxes_id': self.lot_id.tax_id.ids,
                           'weight': self.weight,
                           'barcode': self.barcode})
            self.env['stock.quant'].create({
                'product_id': variant.id,
                'quantity': 1,
                'location_id': self.env.ref('stock.stock_location_stock').id
            })
            self.write({'product_id': variant.id})

    @api.model_create_multi
    def create(self, vals_list):
        result = super(StockPiece, self).create(vals_list)
        for piece in result:
            piece.create_variant()
        return result

    def write(self, vals):
        result = super(StockPiece, self).write(vals)
        if vals and 'product_tmpl_id' in vals and vals['product_tmpl_id']:
            self.create_variant()
        return result

    @api.depends('lot_id', 'lot_id.cost_2', 'lot_id.additional_usd', 'weight')
    def _compute_cost_3(self):
        for piece in self:
            piece.cost_3 = (piece.lot_id.cost_2 + piece.lot_id.additional_usd) * piece.weight
            piece.total_cost = piece.lot_id.cost_2 * piece.weight

    @api.depends('lot_id', 'cost_3', 'lot_id.tax_id', 'lot_id.variant')
    def _compute_price(self):
        currency_model = self.env['res.currency']
        for piece in self:
            price_untaxed = (piece.cost_3 * (piece.lot_id.variant or 1))
            price = price_untaxed + (price_untaxed * piece.lot_id.tax_id.amount / 100)
            currency_mxn = currency_model.browse(self.env.ref('base.MXN').id)
            price_mxn = price * currency_mxn.rate
            piece.price_usd = piece.lot_id.purchase_cost if not price else price
            piece.price_mxn = piece.lot_id.purchase_cost if not price else price_mxn

    def print_sticker(self, print_enabled=True):
        self.create_variant()
        manager = LabelManager()
        data = {'code': self.barcode or "",
                'product': self.product_id.name or "",
                'weight': self.weight,
                'price_usd': str(round(self.price_usd)),
                'price_mxn': str(round(self.price_mxn))}
        label = manager.generate_label_data(data)
        self.write({'raw_data': label.dumpZPL(), 'print_enabled': print_enabled})
