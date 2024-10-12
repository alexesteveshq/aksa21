import logging

from odoo import http
from odoo.http import request, route
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class StaxPaymentController(http.Controller):

    @route('/payment/staxpay/process', type='http', auth='public', methods=['POST'], csrf=False)
    def staxpay_process_transaction(self, **post):
        return request.redirect('/payment/status')

    @http.route('/payment/staxpay/confirm', type='http', auth='public', methods=['POST'], csrf=False)
    def staxpay_webhook(self, **data):
        try:
            request.env['payment.transaction'].sudo()._handle_notification_data('staxpay', data)
            _logger.exception("staxpay payment confirmation received")
        except ValidationError:  # Acknowledge the notification to avoid getting spammed
            _logger.exception("unable to handle the notification data; skipping to acknowledge")
        return ''
