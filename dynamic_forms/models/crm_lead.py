# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    state_partner_id = fields.Many2one('res.country.state')
    dynamic_form_data = fields.Json('Form data')
