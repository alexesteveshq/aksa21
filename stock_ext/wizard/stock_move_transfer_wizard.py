# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMoveTransfer(models.TransientModel):
    _name = 'stock.move.transfer'
    _description = 'Transfer Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner')
    location_id = fields.Many2one('stock.location', string='Origin location')
    location_dest_id = fields.Many2one('stock.location', string='Destination location')

    def create_transfer(self):
        moves = self.env['stock.move'].browse(self._context.get('active_ids'))
        if moves:
            self.env['stock.picking'].create({
                'partner_id': self.partner_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                'move_ids_without_package':
                    [(0, 0, {'product_id': move.product_id.id,
                             'name': 'interco transfer',
                             'location_id': self.location_id.id,
                             'location_dest_id': self.location_dest_id.id,
                             'product_uom_qty': 1}) for move in moves]})
