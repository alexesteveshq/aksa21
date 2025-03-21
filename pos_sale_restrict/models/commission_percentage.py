
from odoo import models, fields


class CommissionPercentage(models.Model):
    _name = 'commission.percentage'
    _description = 'Commission Percentage'

    product_category_id = fields.Many2one('stock.product.category', string='Product category')
    payment_method_id = fields.Many2one('pos.payment.method', string='Payment method')
    value = fields.Float(string='Value')
