odoo.define('pos_ext.ProductScreen', function(require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    var { Gui } = require('point_of_sale.Gui');
    var core = require('web.core');
    var _t = core._t;

    const PosDiscCalcProductScreenVal = ProductScreen => class extends ProductScreen {
        async _onClickPay() {
            var barcodes = []
            for (let line of this.currentOrder.orderlines) {
                barcodes.push(line.product.barcode);
            }
            await this.rpc({
                model: 'stock.quant',
                method: 'search_read',
                args: [[['product_id.barcode', 'in', barcodes], ['quantity', '>=', 1],
                 ['company_id', '=', this.env.pos.company.id]]],
                fields: ['product_id', 'quantity'],
            }).then(async data => {
                var product = ''
                data.forEach(quant => {
                    this.currentOrder.orderlines.forEach(line => {
                        if(line.product.id === quant.product_id[0] && line.quantity > quant.quantity){
                            product = quant.product_id[1]
                        }
                    })
                })
                if (product){
                    Gui.showPopup('ErrorPopup', {
                        title: _t('Not enough stock'),
                        body: _t('Not enough stock for product: ') + product
                    });
                }else{
                    await super._onClickPay();
                }
            });
        }
    }

    Registries.Component.extend(ProductScreen, PosDiscCalcProductScreenVal);
    return ProductScreen;
});
