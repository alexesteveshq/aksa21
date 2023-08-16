# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lot_discount_ids = fields.One2many('lot.discount', 'order_id', string='Lot discount')
    retail_variant = fields.Float(string='Retail variant')

    @api.model_create_multi
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        for order in result:
            if order.retail_variant:
                order.mapped('order_line.product_id').write({'retail_variant': order.retail_variant})
        return result

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals and 'retail_variant' in vals and vals['retail_variant']:
            for order in self:
                order.order_line.mapped('product_id').write({'retail_variant': order.retail_variant})
        return res

    def sell_transfered(self, location_id=False, company_id=False, limit=1000):
        quants = self.env['stock.quant'].search([('location_id', '=', location_id)], limit=limit)
        company = self.env['res.company'].browse(company_id)
        if quants and company_id:
            order = self.env['sale.order'].create(
                {'name': 'Transfered products',
                 'partner_id': company.partner_id.id,
                 'order_line': [
                     (0, 0, {'product_id': quant.product_id.id,
                             'product_uom_qty': quant.available_quantity,
                             'avg_price_calc': 4 if quant.product_id.retail_variant == 6.95 else 2.75})
                     for quant in quants]})
            order.mapped('order_line').onchange_avg_price_calc()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    piece_lot_it = fields.Many2one(related='product_id.lot_id')
    barcode = fields.Char(related='product_id.barcode')
    weight = fields.Float(related='product_id.weight')
    average_price_gram = fields.Float(string='Avg. Price per gram', compute='_compute_average_price_gram', store=True)
    avg_price_calc = fields.Float(string='Avg. Price calc')
    discount = fields.Float()

    @api.onchange('avg_price_calc')
    def onchange_avg_price_calc(self):
        for line in self:
            line.price_unit = line.avg_price_calc * line.weight

    @api.depends('product_id', 'product_id.weight')
    def _compute_average_price_gram(self):
        for line in self:
            if line.product_id and not line.average_price_gram:
                line.average_price_gram = round(line.price_subtotal / (line.product_id.weight or 1), 2)
            else:
                line.average_price_gram = 0

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'order_id.lot_discount_ids',
                 'order_id.lot_discount_ids.lot_id', 'order_id.lot_discount_ids.value')
    def _compute_discount(self):
        super(SaleOrderLine, self)._compute_discount()
        for line in self:
            disc_line = line.order_id.lot_discount_ids.filtered(lambda disc: disc.lot_id == line.product_id.lot_id)
            if disc_line:
                line.discount = disc_line[0].value
