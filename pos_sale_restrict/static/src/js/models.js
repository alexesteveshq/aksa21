odoo.define('pos_sale_restrict.sellers', function (require) {
    "use strict";

var { PosGlobalState, Order, Payment } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

const PosPosGlobalStateCommission = (PosGlobalState) => class PosPosGlobalStateCommission extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.commission_percentage = loadedData['commission_percentage'];
    }
}

Registries.Model.extend(PosGlobalState, PosPosGlobalStateCommission);

});
