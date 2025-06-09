odoo.define('account_reports_legacy.order', function (require) {
    "use strict";

var { Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');
const utils = require('web.utils');
const round_pr = utils.round_precision;

const OrderMulticurrencyAccount = (Order) => class OrderMulticurrencyAccount extends Order {
    get_total_paid() {
        var result = super.get_total_paid(...arguments);
        if (this.new_currency !== undefined && this.new_currency.name === 'USM'){
            return round_pr(this.paymentlines.reduce((function(sum, paymentLine) {
                if (paymentLine.is_done()) {
                    if (paymentLine.payment_method.currency_id[1] === 'MXN'){
                        sum += paymentLine.get_amount() / paymentLine.pos.rate;
                    }else{
                        sum += paymentLine.get_amount();
                    }
                }
                return sum;
            }), 0), this.pos.currency.rounding);
        }
        return result
    }
}

Registries.Model.extend(Order, OrderMulticurrencyAccount);

});
