# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'staxpay':
            return res

        return {
            'api_url': '/payment/staxpay/process',
            'reference': self.reference,
        }
