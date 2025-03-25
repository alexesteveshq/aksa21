
from odoo import models, fields


class CommissionPercentage(models.Model):
    _name = 'commission.percentage'
    _description = 'Commission Percentage'

    code = fields.Char(string='Category code')
    payment_method_id = fields.Many2one('pos.payment.method', string='Payment method')
    value = fields.Float(string='Value')
