odoo.define('pos_ext.chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosExtCustom = (Chrome) =>
        class extends Chrome {
            _onPlaySound({ detail: name }) {
                this.state.sound.src = '';
            }
        };

    Registries.Component.extend(Chrome, PosExtCustom);

    return Chrome;
});