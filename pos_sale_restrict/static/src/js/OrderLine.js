odoo.define('pos_sale_restrict.models', function (require) {
    "use strict";

var { Order, Orderline } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

const PosRestrictOrderline = (Orderline) => class PosRestrictOrderline extends Orderline {
    get_price_currency_with_tax(){
        if ((this.order.new_currency !== undefined && ['USX', 'USM'].includes(this.order.new_currency.name))
        || (['USX', 'USM'].includes(this.pos.currency.name))){
            return this.get_all_prices().priceWithTax * this.pos.rate;
        }
        return this.get_all_prices().priceWithTax;
    }
}
Registries.Model.extend(Orderline, PosRestrictOrderline);

});