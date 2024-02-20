# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class UpdateRate(models.TransientModel):
    _name = 'currency.update.rate'
    _description = 'Update Rate Wizard'

    date = fields.Date(string='Date')
    rate = fields.Float(string='Rate')

    def update_rate(self):
        companies = self.env['res.company'].search([])
        currency = self.env['res.currency'].browse(self._context.get('active_ids'))
        rate_model = self.env['res.currency.rate']
        for company in companies:
            rate = rate_model.search([('name', '=', self.date),
                                      ('company_id', '=', company.id),
                                      ('currency_id', '=', currency.id)])
            if not rate:
                rate_model.sudo().create({'name': self.date,
                                          'currency_id': currency.id,
                                          'company_id': company.id,
                                          'inverse_company_rate': self.rate})
