# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    occupancy_percentage = fields.Float(string='% de Ocupación')

    def _loader_params_pos_session(self):
        result = super()._loader_params_pos_session()
        result['search_params']['fields'].append('occupancy_percentage')
        return result

    def set_occupancy_percentage(self, value):
        """Set the occupancy on this session and propagate the value to all other
        sessions of the same company that started on the same local day."""
        self.ensure_one()
        value = value or 0.0
        from datetime import datetime, timedelta
        import pytz
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        if self.start_at:
            ref_date = pytz.UTC.localize(self.start_at).astimezone(tz).date()
        else:
            ref_date = datetime.now(tz).date()
        day_start_local = tz.localize(datetime.combine(ref_date, datetime.min.time()))
        day_end_local = day_start_local + timedelta(days=1)
        day_start_utc = day_start_local.astimezone(pytz.UTC).replace(tzinfo=None)
        day_end_utc = day_end_local.astimezone(pytz.UTC).replace(tzinfo=None)
        siblings = self.sudo().search([
            ('config_id.company_id', '=', self.config_id.company_id.id),
            ('start_at', '>=', day_start_utc),
            ('start_at', '<', day_end_utc),
        ])
        siblings.write({'occupancy_percentage': value})
        return value

    def get_default_occupancy(self):
        """Value to pre-fill the POS popup with: current session value if set,
        otherwise the latest non-zero occupancy registered for the same company today."""
        self.ensure_one()
        if (self.occupancy_percentage or 0) > 0:
            return self.occupancy_percentage
        from datetime import datetime, timedelta
        import pytz
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        today_local = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_local = today_local + timedelta(days=1)
        today_start_utc = today_local.astimezone(pytz.UTC).replace(tzinfo=None)
        tomorrow_start_utc = tomorrow_local.astimezone(pytz.UTC).replace(tzinfo=None)
        last = self.sudo().search([
            ('config_id.company_id', '=', self.config_id.company_id.id),
            ('start_at', '>=', today_start_utc),
            ('start_at', '<', tomorrow_start_utc),
            ('occupancy_percentage', '>', 0),
        ], order='start_at desc', limit=1)
        return last.occupancy_percentage if last else 0.0

    @api.model
    def get_dashboard_month_avg_occupancy(self):
        """Month average: one value per (company, day) - the latest non-zero - then averaged."""
        from datetime import datetime
        import pytz
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        today_local = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        month_start_utc = today_local.replace(day=1).astimezone(pytz.UTC).replace(tzinfo=None)
        companies = self.env['res.company'].sudo().search([
            ('company_registry', 'in', ['sian_kaan', 'dreams_vista', 'grand_outlet', 'costa_mujeres', 'aventuras'])
        ])
        sessions = self.sudo().search([
            ('config_id.company_id', 'in', companies.ids),
            ('start_at', '>=', month_start_utc),
        ], order='start_at desc')

        values_per_day = {}
        for session in sessions:
            value = session.occupancy_percentage or 0.0
            if value <= 0:
                continue
            start_local = pytz.UTC.localize(session.start_at).astimezone(tz) if session.start_at else None
            if not start_local:
                continue
            key = (session.config_id.company_id.id, start_local.date())
            if key in values_per_day:
                continue  # already have the latest (sorted desc)
            values_per_day[key] = value

        values = list(values_per_day.values())
        return round(sum(values) / len(values), 2) if values else 0.0
