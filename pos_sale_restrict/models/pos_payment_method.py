
from odoo import models, fields


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    company_registry = fields.Char(store=True)
    commission_percentage_ids = fields.One2many('commission.percentage', 'payment_method_id', string='Commission percentages')
