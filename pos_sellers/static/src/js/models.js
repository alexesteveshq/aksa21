odoo.define('pos_ext.sellers', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const PosExtPosGlobalState = (PosGlobalState) => class PosExtPosGlobalState extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.sellers = loadedData['sellers'];
    }
}

Registries.Model.extend(PosGlobalState, PosExtPosGlobalState);
});
