# -*- coding: utf-8 -*-

import logging
from odoo.addons.product.models.product_product import ProductProduct
from odoo import fields, api

_logger = logging.getLogger(__name__)


def uninstall_hook(cr, registry):
    ProductProduct._revert_method("_compute_product_lst_price")
    _logger.info("ProductProduct._compute_product_lst_price method patch reverted!")


def post_load_hook():
    """Patch _compute_product_lst_price calculation for including sale USD price."""

    @api.depends('list_price', 'price_extra')
    @api.depends_context('uom')
    def _compute_product_lst_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse(self._context['uom'])

        for product in self:
            if to_uom:
                list_price = product.uom_id._compute_price(product.list_price, to_uom)
            # PATCH START
            elif product.price_usd:
                list_price = product.price_usd
            # PATCH END
            else:
                list_price = product.list_price
            product.lst_price = list_price + product.price_extra

    ProductProduct._patch_method('_compute_product_lst_price', _compute_product_lst_price)
    _logger.info("ProductProduct._compute_product_lst_price method patched!")