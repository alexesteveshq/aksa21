# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ..LabelManager import LabelManager


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(default='product')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _default_piece_barcode(self):
        return self.env['ir.sequence'].next_by_code('stock_ext.stock_piece')

    list_price = fields.Float(string='List price', compute='_compute_price', store=True, readonly=False)
    pieces_ids = fields.One2many('stock.piece', 'product_id', string='Pieces')
    lot_id = fields.Many2one('stock.lot', string='Lot')
    barcode = fields.Char(default=_default_piece_barcode)
    raw_data = fields.Char(string='Raw data')
    standard_price = fields.Float(compute='_compute_standard_price', store=True, readonly=False)
    total_cost = fields.Float(string='Total Cost', compute='_compute_standard_price', store=True)
    price_usd = fields.Float(string='Price USD', compute='_compute_price', store=True, readonly=False)
    price_mxn = fields.Float(string='Price MXN', compute='_compute_price', store=True, readonly=False)
    print_enabled = fields.Boolean(string='Print enabled')
    scale_created = fields.Boolean(string='Scale created')

    def name_get(self):
        res = []
        for product in self:
            name = product.name
            if product.scale_created:
                name = "%s (%s) |%s|" % (product.categ_id.name, product.weight or '0.0', product.barcode)
            res += [(product.id, name)]
        return res

    @api.model_create_multi
    def create(self, vals_list):
        result = super(ProductProduct, self).create(vals_list)
        for piece in result:
            piece.name = piece.barcode
            if piece.scale_created:
                self.env['stock.quant'].create({
                    'product_id': piece.id,
                    'quantity': 1,
                    'location_id': self.env.ref('stock.stock_location_stock').id})
        return result

    @api.depends('lot_id', 'lot_id.cost_2', 'lot_id.additional_usd', 'weight')
    def _compute_standard_price(self):
        for piece in self:
            piece.standard_price = (piece.lot_id.cost_2 + piece.lot_id.additional_usd) * piece.weight
            piece.total_cost = piece.lot_id.cost_2 * piece.weight

    @api.depends('lot_id', 'standard_price', 'lot_id.tax_id', 'lot_id.variant')
    def _compute_price(self):
        currency_model = self.env['res.currency']
        for piece in self:
            price_untaxed = (piece.standard_price * (piece.lot_id.variant or 1))
            price = price_untaxed + (price_untaxed * piece.lot_id.tax_id.amount / 100)
            currency_mxn = currency_model.browse(self.env.ref('base.USD').id)
            price_mxn = price * currency_mxn.inverse_rate
            piece.price_usd = piece.lot_id.purchase_cost if not price else price
            piece.price_mxn = piece.lot_id.purchase_cost if not price else price_mxn
            piece.list_price = piece.standard_price * (piece.lot_id.variant or 1) * currency_mxn.inverse_rate

    def print_sticker(self, print_enabled=True, retail=False):
        manager = LabelManager()
        data = {'code': self.barcode or "",
                'product': self.categ_id.name or "",
                'weight': self.weight,
                'price_usd': str(round(self.price_usd)),
                'price_mxn': str(round(self.price_mxn))}
        if retail:
            variants = self.env['piece.variant'].search([])
            variants = variants.filtered(lambda var: var.min_weight <= self.weight <= var.max_weight)
            currency_mxn = self.env['res.currency'].browse(self.env.ref('base.USD').id)
            if variants:
                fixed_price = self.env['ir.config_parameter'].sudo().get_param('stock_ext.retail_variant_amount')
                retail_price = (float(fixed_price) * self.weight) * variants[0].value
                price = retail_price - (retail_price * 15/100)
                price_taxed = price + (price * self.lot_id.tax_id.amount / 100)
                data.update({'price_usd': str(round(price_taxed)),
                             'price_mxn': str(round(round(price_taxed) * currency_mxn.inverse_rate))})
        label = manager.generate_label_data(data)
        self.write({'raw_data': label.dumpZPL(), 'print_enabled': print_enabled})

    def print_sticker_wholesale(self):
        for piece in self:
            piece.print_sticker()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        name = name.upper()
        return super(ProductProduct, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
