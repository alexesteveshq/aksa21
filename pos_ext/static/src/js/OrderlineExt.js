odoo.define('pos_ext.OrderlineExt', function(require) {
	"use strict";

	var { Orderline } = require('point_of_sale.models');
	var Registries = require('point_of_sale.Registries');

	const PosExtLine = (Orderline) => class PosExtLine extends Orderline {
		export_for_printing(){
		    var result = super.export_for_printing(...arguments);
		    result.product_name_wrapped[0] = result.product_name_wrapped[0] +
		    " [" + this.product.barcode + "]"
		    return result
		}
    }
	Registries.Model.extend(Orderline, PosExtLine);
});