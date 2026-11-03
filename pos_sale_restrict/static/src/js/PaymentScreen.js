odoo.define('pos_sale_restrict.PaymentScreen', function(require) {
	"use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");


    const PosPaymentScreenCommission = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            useListener('set-commission-percentage', this.setCommissionPercentage);
            useListener('validate-price', () => this.showCommissionPriceMessage(false));
            this.commission_percentage = this.env.pos.commission_percentage
        }

        checkCommissionPrice() {
            // Codigos de categoria con precio minimo: los configurados en cualquier metodo de pago del TPV.
            // Asi un metodo sin comisiones (p.ej. Banamex) ya no se salta la validacion.
            const restricted_codes = new Set();
            for (const method of this.env.pos.payment_methods) {
                for (const commission of method.commission_percentage_ids || []) {
                    if (commission.code) restricted_codes.add(commission.code);
                }
            }
            for (const line of this.currentOrder.orderlines) {
                const category_code = line.product.category_code || '';
                if (![...restricted_codes].some(code => category_code.includes(code))) continue;
                var method_percentage = 0
                for (const pay_line of this.paymentLines) {
                    for (const commission of pay_line.payment_method.commission_percentage_ids) {
                        if (commission.code && category_code.includes(commission.code)){
                            method_percentage += commission.value
                            break
                        }
                    }
                }
                if (this.paymentLines.length) method_percentage /= this.paymentLines.length
                const cost = line.product.standard_price * line.get_quantity()
                const min_price = cost * (1 + (this.commission_percentage + method_percentage) * 0.01)
                const price = line.get_price_currency_with_tax()
                if (price >= 0 && price < min_price){
                    return false;
                }
            }
            return true
        }

        showCommissionPriceMessage() {
            if (this.checkCommissionPrice()){
                this.showPopup('ConfirmPopup',{
                    'title': this.env._t("Minimal price"),
                    'body':  this.env._t("Product price is correct"),
                });
            }else{
                this.showPopup('ErrorPopup',{
                    'title': this.env._t("Minimal price"),
                    'body':  this.env._t("Product sale price is lower than the minimum price"),
                });
            }
        }

        async validateOrder(isForceValidate) {
            if (this.checkCommissionPrice()){
                await super.validateOrder(...arguments);
            }else{
                this.showPopup('ErrorPopup',{
                    'title': this.env._t("Minimal price"),
                    'body':  this.env._t("Product sale price is lower than the minimum price"),
                });
            }
        }

        setCommissionPercentage(commission_percentage) {
            this.currentOrder.commission_percentage = commission_percentage;
        }
	}
	Registries.Component.extend(PaymentScreen, PosPaymentScreenCommission);
});
