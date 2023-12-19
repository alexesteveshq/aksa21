odoo.define('pos_ext.PaymentScreen', function(require) {
	"use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");


    const PosExtPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            useListener('set-seller', this.setSeller);
            this.sellers = this.env.pos.sellers.filter(
            seller => this.env.pos.config.payment_seller_ids.includes(seller.id));
        }

        setSeller(seller) {
            this.currentOrder.seller_id = seller.detail.id;
        }
	}
	Registries.Component.extend(PaymentScreen, PosExtPaymentScreen);
});
