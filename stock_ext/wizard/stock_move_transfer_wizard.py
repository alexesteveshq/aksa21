# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMoveTransfer(models.TransientModel):
    _name = 'stock.move.transfer'
    _description = 'Transfer Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner')
    location_id = fields.Many2one('stock.location', string='Origin location')
    location_dest_id = fields.Many2one('stock.location', string='Destination location')

    def create_transfer(self):
        quants = self.env['stock.quant'].sudo().browse(self._context.get('active_ids'))
        picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'INT')])
        if quants and picking_type:
            transfer = self.env['stock.picking'].sudo().create({
                    'partner_id': self.partner_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'picking_type_id': picking_type.id,
                    'move_ids_without_package':
                        [(0, 0, {'product_id': quant.product_id.id,
                                 'name': 'interco transfer',
                                 'location_id': self.location_id.id,
                                 'location_dest_id': self.location_dest_id.id,
                                 'product_uom_qty': 1}) for quant in quants]})
            transfer.company_id = self.env.company.id
