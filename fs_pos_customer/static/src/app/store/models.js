/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";


patch(Order.prototype, {
    async pay() {
        if (!this.pos.get_order().partner) {
            return this.env.services.popup.add(ErrorPopup, {
                title: _t("Customer Is Required"),
                body: _t(
                    "Please select customer!"
                ),
            });
        }
        await super.pay()
    }
});