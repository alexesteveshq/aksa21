odoo.define('pos_ext.prevent_add', function(require) {
	"use strict";

	var { Order } = require('point_of_sale.models');
	var { Gui } = require('point_of_sale.Gui');
	var Registries = require('point_of_sale.Registries');
	var core = require('web.core');
	var _t = core._t;

	const PosExt = (Order) => class PosExt extends Order {
		async add_product(product, options){
		    const avlProduct = await this.pos.env.services.rpc({
                model: 'product.product',
                method: 'search_read',
                args: [[['barcode', '=', product.barcode]]],
                fields: ['qty_available'],
            })
		    if (avlProduct[0].qty_available === 0){
		        Gui.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('This product is not available anymore')
                });
                return
		    }
            super.add_product(...arguments);
		}
    }
	Registries.Model.extend(Order, PosExt);
});
