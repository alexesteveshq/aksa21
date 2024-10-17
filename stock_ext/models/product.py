# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ..LabelManager import LabelManager
import re


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(default='product')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _default_piece_barcode(self):
        return self.env['ir.sequence'].next_by_code('stock_ext.stock_piece')

    weight = fields.Float(tracking=True)
    list_price = fields.Float(string='List price', compute='_compute_price', store=True, readonly=False,
                              tracking=True)
    pieces_ids = fields.One2many('stock.piece', 'product_id', string='Pieces')
    lot_id = fields.Many2one('stock.lot', string='Lot', tracking=True)
    barcode = fields.Char(default=_default_piece_barcode, tracking=True)
    raw_data = fields.Char(string='Raw data')
    standard_price = fields.Float(compute='_compute_standard_price', store=True, readonly=False,
                                  tracking=True, company_dependent=False,)
    total_cost = fields.Float(string='Total Cost', compute='_compute_standard_price', store=True)
    price_usd = fields.Float(string='Price USD', compute='_compute_price', store=True, readonly=False,
                             tracking=True)
    price_mxn = fields.Float(string='Price MXN', compute='_compute_price', store=True, readonly=False,
                             tracking=True)
    print_enabled = fields.Boolean(string='Print enabled')
    print_queue = fields.Integer(string='Print queue')
    scale_created = fields.Boolean(string='Scale created')
    cost_retail_calculation = fields.Boolean(string='Cost retail calculation', tracking=True)
    force_sticker_update = fields.Boolean(string='Force sticker update', tracking=True)
    retail_variant = fields.Float(string='Retail variant', default=1, tracking=True)
    retail_price_untaxed = fields.Float(string='Retail price (untaxed)', tracking=True,
                                        compute='_compute_retail_price_untaxed', store=True)
    retail_price_untaxed_usd = fields.Float(string='Retail price USD (untaxed)', tracking=True,
                                            compute='_compute_retail_price_untaxed_usd', store=True)
    price_update = fields.Boolean(string='Price update', default=True)
    category_id = fields.Many2one('stock.product.category', string='category')

    @api.depends('retail_variant', 'weight', 'lst_price', 'cost_retail_calculation')
    def _compute_retail_price_untaxed(self):
        variants = self.env['piece.variant'].search([])
        currency_usx = self.env['res.currency'].search([('name', '=', 'USX')])
        for product in self:
            if self._context.get('import_file') or not product.price_update:
                continue
            else:
                variant = variants.filtered(lambda var: var.min_weight <= product.weight <= var.max_weight)
                currency_mxr = self.env['res.currency'].search([('name', '=', 'MXR')])
                if product.cost_retail_calculation and product.retail_variant:
                    price = product.standard_price * float(product.retail_variant)
                    price_currency = price * currency_mxr.inverse_rate
                    product.retail_price_untaxed = price_currency / 1.16
                elif variant and product.retail_variant:
                    price = (float(product.retail_variant) * product.weight) * variant.value
                    price = price - (price * 15 / 100)
                    product.retail_price_untaxed = (price * currency_usx.inverse_rate) / 1.16
                elif product.cost_retail_calculation:
                    product.retail_price_untaxed = product.lst_price * currency_mxr.inverse_rate

    @api.depends('retail_price_untaxed')
    def _compute_retail_price_untaxed_usd(self):
        currency_usd = self.env['res.currency'].search([('name', '=', 'USR')])
        for product in self:
            if self._context.get('import_file') or not product.price_update:
                continue
            else:
                product.retail_price_untaxed_usd = product.retail_price_untaxed / currency_usd.inverse_rate

    @api.model_create_multi
    def create(self, vals_list):
        result = super(ProductProduct, self).create(vals_list)
        for piece in result:
            if piece.scale_created:
                piece.name = piece.barcode
                self.env['stock.quant'].create({
                    'product_id': piece.id,
                    'quantity': 1,
                    'location_id': self.env.ref('stock.stock_location_stock').id})
        return result

    @api.depends('lot_id', 'lot_id.cost_2', 'lot_id.additional_usd', 'weight')
    def _compute_standard_price(self):
        for piece in self:
            if not self._context.get('import_file') and not piece.cost_retail_calculation:
                piece.standard_price = (piece.lot_id.cost_2 + piece.lot_id.additional_usd) * piece.weight
                piece.total_cost = piece.lot_id.cost_2 * piece.weight

    @api.depends('lot_id', 'standard_price', 'lot_id.tax_id', 'lot_id.variant')
    def _compute_price(self):
        currency_model = self.env['res.currency']
        for piece in self:
            if self._context.get('import_file') or not piece.price_update:
                continue
            else:
                price_untaxed = (piece.standard_price * (piece.lot_id.variant or 1))
                price = price_untaxed + (price_untaxed * piece.lot_id.tax_id.amount / 100)
                currency_mxn = currency_model.browse(self.env.ref('base.USD').id)
                price_mxn = price * currency_mxn.inverse_rate
                piece.price_usd = piece.lot_id.purchase_cost if not price else price
                piece.price_mxn = piece.lot_id.purchase_cost if not price else price_mxn
                piece.list_price = piece.standard_price * (piece.lot_id.variant or 1) * currency_mxn.inverse_rate

    def update_price_from_sticker(self):
        for product in self.filtered(lambda prod: prod.raw_data):
            pattern_mxn = re.compile(r'MXN\s*([\d.]+)')
            matches_mxn = pattern_mxn.search(product.raw_data)
            pattern_usd = re.compile(r'USD\s*([\d.]+)')
            matches_usd = pattern_usd.search(product.raw_data)
            if matches_mxn:
                mxn_value = matches_mxn.group(1)
                product.retail_price_untaxed = float(mxn_value) / 1.16
            if matches_usd:
                usd_value = matches_usd.group(1)
                product.retail_price_untaxed_usd = float(usd_value) / 1.16

    def print_sticker(self, print_enabled=True):
        if not self.raw_data or self.force_sticker_update:
            manager = LabelManager()
            data = {'code': self.barcode or "",
                    'product': self.name,
                    'weight': self.weight,
                    'price_usd': str(round(self.price_usd)),
                    'price_mxn': str(round(self.price_mxn))}
            data.update({'price_usd': str(round(self.retail_price_untaxed_usd * 1.16)),
                         'price_mxn': str(round(self.retail_price_untaxed * 1.16))})
            label = manager.generate_label_data(data)
            self.write({'raw_data': label.dumpZPL()})
        self.write({'print_enabled': print_enabled,
                    'print_queue': int(self.qty_available)})

    def print_sticker_wholesale(self):
        for piece in self:
            piece.print_sticker()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        name = name.upper()
        return super(ProductProduct, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
