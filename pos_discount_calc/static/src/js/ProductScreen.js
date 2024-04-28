odoo.define('pos_discount_calc.ProductScreen', function(require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PosDiscCalcProductScreen = ProductScreen => class extends ProductScreen {
        _setValue(val) {
            if (this.currentOrder.get_selected_orderline()) {
                if (this.env.pos.numpadMode === 'quantity') {
                    const result = this.currentOrder.get_selected_orderline().set_quantity(val);
                    if (!result) NumberBuffer.reset();
                } else if (this.env.pos.numpadMode === 'discount') {
                    this.currentOrder.get_selected_orderline().set_discount(val);
                } else if (this.env.pos.numpadMode === 'price') {
                    var order_line = this.currentOrder.get_selected_orderline();
                    var total_price = order_line.product.retail_price_untaxed_usd
                    if (this.currentOrder.pricelist.currency_id[1] !== 'USX'){
                        total_price = order_line.product.retail_price_untaxed
                    }
                    order_line.price_manually_set = true;
                    var discount = ((total_price - (parseFloat(val) / 1.16)) / total_price) * 100
                    this.currentOrder.get_selected_orderline().set_discount(+discount.toFixed(2));
                    order_line.set_unit_price(val);
                }
            }
        }
    }

    Registries.Component.extend(ProductScreen, PosDiscCalcProductScreen);
    return ProductScreen;
});
