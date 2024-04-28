from odoo import _, models, fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    price_manually_set = fields.Boolean(string='Manually set')

    def _export_for_ui(self, orderline):
        result = super(PosOrderLine, self)._export_for_ui(orderline)
        result['price_manually_set'] = orderline.price_manually_set
        return result
