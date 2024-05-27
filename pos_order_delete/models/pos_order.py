# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_cancel(self):
        if not self.env.user.has_group('pos_order_delete.group_delete_pos_order'):
            return super()._unlink_except_draft_or_cancel()
        else:
            for order in self:
                for line in order.lines:
                    line.qty = line.qty * -1
                order._create_order_picking()
                order.payment_ids.unlink()
