from odoo import models, fields
from odoo.addons.payment_sips import const

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    # Add 'staxpay' as a selection option to the 'provider' field
    code = fields.Selection(selection_add=[('staxpay', 'StaxPay')], ondelete={'staxpay': 'set default'})

    # Add fields specific to the StaxPay configuration
    staxpay_secret_key = fields.Char(string='StaxPay Secret Key')
    staxpay_public_key = fields.Char(string='StaxPay Public Key')

    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'staxpay':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'staxpay':
            return default_codes
        return const.DEFAULT_PAYMENT_METHODS_CODES
