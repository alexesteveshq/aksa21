odoo.define('pos_ext.sellers', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const PosSellerOrder = (Order) => class PosSellerOrder extends Order {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.seller_id = this.seller_id;
        return json;
    }
    export_for_printing(){
        var receipt = super.export_for_printing();
        receipt['seller_name'] = this.seller_name
        return receipt
    }
}

Registries.Model.extend(Order, PosSellerOrder);

const PosExtPosGlobalState = (PosGlobalState) => class PosExtPosGlobalState extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.sellers = loadedData['sellers'];
    }
}

Registries.Model.extend(PosGlobalState, PosExtPosGlobalState);
});
