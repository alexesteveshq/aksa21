odoo.define('pos_ext.PaymentScreen', function(require) {
	"use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');


    const PosExtPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            this.sellers = this.env.pos.sellers.filter(
            seller => this.env.pos.config.payment_seller_ids.includes(seller.id));
        }
	}
	Registries.Component.extend(PaymentScreen, PosExtPaymentScreen);
});
