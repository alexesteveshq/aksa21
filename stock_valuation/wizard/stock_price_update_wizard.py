# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

# IVA con el que se imprime el precio de la etiqueta (ver product.product._get_sticker_zpl)
STICKER_TAX = 1.16


class StockPriceUpdateWizard(models.TransientModel):
    _name = 'stock.price.update.wizard'
    _description = 'Price Update Wizard'

    company_id = fields.Many2one('res.company', string='Store', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')
    category_ids = fields.Many2many('stock.product.category', string='Categories', required=True)
    percentage = fields.Float(string='Percentage (%)',
                              help='Positive values increase the price, negative values decrease it.')
    print_labels = fields.Boolean(string='Print labels')
    piece_count = fields.Integer(string='Pieces to update', compute='_compute_piece_count')

    @api.depends('company_id', 'date_start', 'date_end', 'category_ids')
    def _compute_piece_count(self):
        for wizard in self:
            wizard.piece_count = len(wizard._get_stock_quantities())

    def _get_stock_quantities(self):
        """Piezas con existencia en la tienda que cumplen los filtros: {product_id: cantidad}"""
        self.ensure_one()
        if not self.category_ids:
            return {}
        domain = [('company_id', '=', self.company_id.id),
                  ('location_id.usage', '=', 'internal'),
                  ('product_id.category_id', 'in', self.category_ids.ids)]
        if self.date_start:
            domain.append(('product_id.create_date', '>=', datetime.combine(self.date_start, time.min)))
        if self.date_end:
            domain.append(('product_id.create_date', '<', datetime.combine(self.date_end + timedelta(days=1),
                                                                           time.min)))
        groups = self.env['stock.quant']._read_group(domain, ['product_id', 'quantity:sum'], ['product_id'])
        return {group['product_id'][0]: group['quantity'] for group in groups if group['quantity'] > 0}

    def action_update_prices(self):
        self.ensure_one()
        if not self.category_ids:
            raise UserError(_('Select at least one category.'))
        if not self.percentage:
            raise UserError(_('Set the percentage to apply.'))
        if self.percentage <= -100:
            raise UserError(_('The percentage cannot be -100% or lower.'))
        quantities = self._get_stock_quantities()
        if not quantities:
            raise UserError(_('There are no pieces in stock matching the filters.'))
        factor = 1 + self.percentage / 100
        products = self.env['product.product'].browse(quantities).with_context(increase_price=True)
        # Sin precio de etiqueta no hay nada que actualizar ni que imprimir
        no_price = products.filtered(lambda p: not round(p.retail_price_untaxed * STICKER_TAX)
                                     and not round(p.retail_price_untaxed_usd * STICKER_TAX))
        products -= no_price
        for product in products:
            # Se parte del precio con IVA redondeado, que es el que sale en la etiqueta
            price_mxn = round(round(product.retail_price_untaxed * STICKER_TAX) * factor)
            price_usd = round(round(product.retail_price_untaxed_usd * STICKER_TAX) * factor)
            product.write({'retail_price_untaxed': price_mxn / STICKER_TAX,
                           'retail_price_untaxed_usd': price_usd / STICKER_TAX})
            vals = {'raw_data': product._get_sticker_zpl()}
            if self.print_labels:
                vals.update({'print_enabled': True, 'print_queue': int(quantities[product.id])})
            product.write(vals)
        message = _('%(count)s pieces updated by %(percentage)s%%.',
                    count=len(products), percentage=self.percentage)
        if no_price:
            message += ' ' + _('%(count)s pieces without price were skipped.', count=len(no_price))
        if self.print_labels:
            message += ' ' + _('Labels sent to the print queue.')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Price update'),
                'message': message,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
