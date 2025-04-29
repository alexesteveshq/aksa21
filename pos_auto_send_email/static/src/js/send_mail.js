odoo.define('pos_auto_send_email.ReceiptScreen', function(require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    var models = require('point_of_sale.models');

    const PosResReceiptScreen1 = ReceiptScreen =>
        class extends ReceiptScreen {
            handleAutoPrint() {
                super.handleAutoPrint();
                if (this.env.pos.config.send_auto_email) {
                    this.onSendEmail();
                }
           }
        };

    Registries.Component.extend(ReceiptScreen, PosResReceiptScreen1);

    return ReceiptScreen;
});