odoo.define('pos_discount_calc.models', function (require) {
    "use strict";

var { Order, Orderline } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

const DiscCalcOrderline = (Orderline) => class DiscCalcOrderline extends Orderline {
    get_all_prices(qty = this.get_quantity()){
        if (!this.price_manually_set){
            var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        }else{
            var price_unit = this.get_unit_price() / 1.16;
        }
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes_ids = this.tax_ids || product.taxes_id;
        taxes_ids = _.filter(taxes_ids, t => t in this.pos.taxes_by_id);
        var taxdetail = {};
        var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);

        var all_taxes = this.compute_all(product_taxes, price_unit, qty, this.pos.currency.rounding);
        var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), qty, this.pos.currency.rounding);
        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = {
                amount: Math.round(tax.amount),
                base: tax.base,
            };
        });

        return {
            "priceWithTax": Math.round(all_taxes.total_included),
            "priceWithoutTax": Math.round(all_taxes.total_excluded),
            "priceWithTaxBeforeDiscount": Math.round(all_taxes_before_discount.total_included),
            "priceWithoutTaxBeforeDiscount": Math.round(all_taxes_before_discount.total_excluded),
            "tax": Math.round(taxtotal),
            "taxDetails": taxdetail,
            "tax_percentages": product_taxes.map((tax) => tax.amount),
        };
    }
}
Registries.Model.extend(Orderline, DiscCalcOrderline);

});