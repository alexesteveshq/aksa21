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
                model: 'stock.quant',
                method: 'search_read',
                args: [[['product_id.barcode', '=', product.barcode], ['quantity', '>=', 1],
                 ['company_id', '=', product.pos.company.id]]],
                fields: ['id'],
            })
		    if (!avlProduct.length){
		        Gui.showPopup('ErrorPopup', {
                    title: _t('Error'),
                    body: _t('This product is not available')
                });
                return
		    }
            super.add_product(...arguments);
		}
    }
	Registries.Model.extend(Order, PosExt);
});
