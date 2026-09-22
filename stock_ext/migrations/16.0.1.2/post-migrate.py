# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo import api, SUPERUSER_ID

from odoo.addons.stock_ext.models.product import DEFAULT_RETAIL_USD_RATE

_logger = logging.getLogger(__name__)

USD_IN_LABEL = re.compile(r'USD\s*([\d.]+)')

# Por debajo de este factor la diferencia entre la etiqueta y el precio actual es
# un cambio de precio al que no se le regenero el ZPL, y el bueno es el precio.
# Por encima es un producto recalculado sin el multiplicador de retail, que lo
# deja dividido por ~18, y el bueno es el de la etiqueta.
MIN_FACTOR = 3.0


def _set_retail_usd_rate(env):
    config = env['ir.config_parameter'].sudo()
    if config.get_param('stock_ext.retail_usd_rate'):
        return
    config.set_param('stock_ext.retail_usd_rate', str(DEFAULT_RETAIL_USD_RATE))
    _logger.warning("stock_ext.retail_usd_rate fijado a %s", DEFAULT_RETAIL_USD_RATE)


def _normalize_usx(cr):
    # El unico consumidor que le queda a la tasa de USX es converted_currency del
    # POS, que multiplica un precio que ya viene en dolares: ahi tiene que ser 1.0.
    cr.execute("""UPDATE res_currency_rate r
                     SET rate = 1.0, write_date = now() AT TIME ZONE 'UTC'
                    FROM res_currency c
                   WHERE c.id = r.currency_id AND c.name = 'USX' AND r.rate != 1.0
               RETURNING r.company_id, r.name""")
    for company_id, date in cr.fetchall():
        _logger.warning("USX: compania %s, tasa del %s normalizada a 1.0", company_id, date)


def _repair_prices(env):
    cr = env.cr
    cr.execute("""SELECT id, barcode, raw_data, retail_price_untaxed_usd
                    FROM product_product
                   WHERE raw_data IS NOT NULL AND retail_price_untaxed_usd > 0""")
    product_ids = []
    for product_id, barcode, raw_data, price_usd in cr.fetchall():
        match = USD_IN_LABEL.search(raw_data)
        if not match:
            continue
        on_label = float(match.group(1))
        in_pos = round(float(price_usd) * 1.16)
        if not on_label or not in_pos:
            continue
        if max(on_label / in_pos, in_pos / on_label) < MIN_FACTOR:
            continue
        product_ids.append(product_id)
        _logger.warning("%s: precio %s, etiqueta %s, se restaura el de la etiqueta",
                        barcode, in_pos, on_label)
    if not product_ids:
        _logger.warning("Ningun producto descuadrado respecto a su etiqueta")
        return
    env['product.product'].browse(product_ids).update_price_from_sticker()
    _logger.warning("%d productos restaurados desde su etiqueta", len(product_ids))


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    _set_retail_usd_rate(env)
    _normalize_usx(cr)
    _repair_prices(env)
    env.flush_all()
