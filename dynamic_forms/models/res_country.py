# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class CountryState(models.Model):
    _inherit = 'res.country.state'

    def get_states_published(self):
        partners = self.env['res.partner'].search([('is_published', '=', True)])
        states = self.env['res.country.state'].search([('id', 'in', partners.mapped('state_id.id'))])
        return [{'id': state.id, 'display_name': state.name} for state in states]
