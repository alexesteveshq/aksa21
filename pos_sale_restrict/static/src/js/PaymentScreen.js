odoo.define('pos_sale_restrict.PaymentScreen', function(require) {
	"use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");


    const PosPaymentScreenCommission = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            useListener('set-commission-percentage', this.setCommissionPercentage);
            this.commission_percentage = this.env.pos.commission_percentage
        }

        async validateOrder(isForceValidate) {
            var commission_price = 0
            for (const line of this.currentOrder.orderlines) {
                for (const pay_line of this.paymentLines) {
                    for (const commission of pay_line.payment_method.commission_percentage_ids) {
                        if (line.product.category_code.includes(commission.code)){
                            commission_price += (line.product.standard_price * (commission.value * 0.01)) +
                             (line.product.standard_price * (this.commission_percentage * 0.01))
                        }
                    }
                }
                if (line.get_price_currency_with_tax() >= 0 &&
                 commission_price > 0 && (line.get_price_currency_with_tax() < (line.product.standard_price + commission_price))){
                    this.showPopup('ErrorPopup',{
                        'title': this.env._t("Minimal price"),
                        'body':  this.env._t("Product sale price is lower than the minimum price"),
                    });
                    return;
                }
                commission_price = 0
            }
            await super.validateOrder(...arguments);
        }

        setCommissionPercentage(commission_percentage) {
            this.currentOrder.commission_percentage = commission_percentage;
        }
	}
	Registries.Component.extend(PaymentScreen, PosPaymentScreenCommission);
});
