/** @odoo-module **/

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

const SalesDashboard = registry.category("actions").get("sales_dashboard_js_action");

patch(SalesDashboard.prototype, "pos_occupancy.SalesDashboard", {
    setup() {
        this._super(...arguments);
        this.state.monthAvgOccupancy = 0;
    },

    async loadSalesData() {
        await this._super(...arguments);
        try {
            const avg = await this.orm.call(
                "pos.session",
                "get_dashboard_month_avg_occupancy",
                []
            );
            this.state.monthAvgOccupancy = avg || 0;
        } catch (e) {
            console.warn("pos_occupancy: failed to load month avg occupancy", e);
        }
    },
});
