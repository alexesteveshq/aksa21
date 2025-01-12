odoo.define('pos_ext.rates', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

const PosPosGlobalStateRates = (PosGlobalState) => class PosPosGlobalStateRates extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.rate = loadedData['rate'];
    }
}

Registries.Model.extend(PosGlobalState, PosPosGlobalStateRates);
});
