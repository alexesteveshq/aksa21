odoo.define('pos_ext.multi_currency', function(require) {
	"use strict";

	var { Order } = require('point_of_sale.models');
	var Registries = require('point_of_sale.Registries');
	var core = require('web.core');
	var utils = require('web.utils');
	var round_pr = utils.round_precision;
	var _t = core._t;

	const MultiCurr = (Order) => class MultiCurr extends Order {
		add_paymentline(payment_method) {
		    const result = super.add_paymentline(...arguments);
		    if (result.order.pricelist.currency_id[1] === 'USM'){
		        if (result.payment_method.currency_id[1] === 'MXN'){
		            result.set_amount(result.amount * this.pos.rate);
		        }
		    }
		    return result
		}
		get_change(paymentline) {
		    var result = super.get_change(...arguments);
		    if (this.pricelist.currency_id[1] === 'USM'){
		        result = 0;
		    }
		    return result
		}
		get_due(paymentline) {
		    if (this.pricelist.currency_id[1] === 'USM'){
                var due = this.get_total_with_tax();
                var lines = this.paymentlines;
                for (var i = 0; i < lines.length; i++) {
                    if (lines[i] === paymentline) {
                        break;
                    } else {
                        if (lines[i].payment_method.currency_id[1] === 'MXN'){
                            due -= lines[i].get_amount() / this.pos.rate;
                        }else{
                            due -= lines[i].get_amount();
                        }
                    }
                }
                return round_pr(due, this.pos.currency.rounding);
            }
            return super.get_due(...arguments);
        }
    }
	Registries.Model.extend(Order, MultiCurr);
});
