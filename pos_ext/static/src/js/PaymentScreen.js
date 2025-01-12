odoo.define('pos_ext.PaymentScreenFilter', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    const FilterPayment = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            if (this.env.pos.currency.name !== 'USM'){
                var custom_curr = this.env.pos.currency.name === 'USX' ? 'USD' : 'MXN';
                this.payment_methods_from_config = this.env.pos.payment_methods.filter(method=>method.currency_id[1] === custom_curr && this.env.pos.config.payment_method_ids.includes(method.id));
            }
        };
        async selectPartner() {
            const currentPartner = this.currentOrder.get_partner();
            const { confirmed, payload: newPartner } = await this.showTempScreen(
                'PartnerListScreen',
                { partner: currentPartner }
            );
            if (this.currentOrder.pricelist.currency_id[1] !== 'MXR' && confirmed){
                this.currentOrder.set_partner(newPartner);
            }
            else if (confirmed) {
                this.currentOrder.set_partner(newPartner);
                this.currentOrder.updatePricelist(newPartner);
            }
        };
    }

    Registries.Component.extend(PaymentScreen, FilterPayment);

    return PaymentScreen;
});
