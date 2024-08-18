# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class RealStateProperty(models.Model):
    _name = 'real.state.property'
    _description = 'Real State Property'

    name = fields.Char(string='Name')
    image = fields.Many2one('ir.attachment', string='Image')
    state = fields.Selection([('available', 'Available'), ('not_available', 'Not available')], string='State',
                             default='available')
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
