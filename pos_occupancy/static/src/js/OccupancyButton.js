odoo.define('pos_occupancy.OccupancyButton', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require('web.core');

    class OccupancyButton extends PosComponent {
        get currentValue() {
            return this.env.pos.pos_session.occupancy_percentage || 0;
        }

        get displayLabel() {
            const value = this.currentValue;
            if (value > 0) {
                return _.str.sprintf(_t('Ocupación: %s%%'), this._format(value));
            }
            return _t('% Ocupación');
        }

        _format(value) {
            return Number.isInteger(value) ? value : Number(value).toFixed(2);
        }

        async onClick() {
            let startingValue = this.currentValue;
            if (!startingValue) {
                try {
                    startingValue = await this.rpc({
                        model: 'pos.session',
                        method: 'get_default_occupancy',
                        args: [[this.env.pos.pos_session.id]],
                    });
                } catch (e) {
                    startingValue = 0;
                }
            }
            const { confirmed, payload } = await this.showPopup('NumberPopup', {
                title: _t('% de Ocupación'),
                body: _t('Indica el porcentaje de ocupación para esta sesión'),
                startingValue: startingValue || 0,
                isInputSelected: true,
                confirmText: _t('Aceptar'),
                cancelText: _t('Cancelar'),
            });
            if (!confirmed) return;

            const raw = parseFloat((payload || '0').toString().replace(',', '.'));
            if (isNaN(raw) || raw < 0 || raw > 100) {
                this.showPopup('ErrorPopup', {
                    title: _t('Valor inválido'),
                    body: _t('Introduce un porcentaje entre 0 y 100.'),
                });
                return;
            }

            await this.rpc({
                model: 'pos.session',
                method: 'set_occupancy_percentage',
                args: [[this.env.pos.pos_session.id], raw],
            });

            this.env.pos.pos_session.occupancy_percentage = raw;
            this.render(true);
            this.showNotification(_t('Ocupación guardada'), 2000);
        }
    }
    OccupancyButton.template = 'pos_occupancy.OccupancyButton';

    Registries.Component.add(OccupancyButton);

    return OccupancyButton;
});
