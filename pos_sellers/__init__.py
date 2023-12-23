# -*- coding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID


def set_sellers(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    orders = env['pos.order'].search([])
    for order in orders:
        order.seller_id = order.company_id.partner_id
