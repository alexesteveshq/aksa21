# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz

from odoo import models


COMPANY_REGISTRIES = ['sian_kaan', 'dreams_vista', 'grand_outlet', 'costa_mujeres', 'aventuras']


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_dashboard_data(self, usr_start_date=None, usr_end_date=None):
        result = super().get_dashboard_data(usr_start_date=usr_start_date, usr_end_date=usr_end_date)

        tz = pytz.timezone(self.env.user.tz or 'UTC')
        now_local = datetime.now(tz)
        today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_local = today_local + timedelta(days=1)
        month_start_local = today_local.replace(day=1)

        today_start_utc = today_local.astimezone(pytz.UTC).replace(tzinfo=None)
        tomorrow_start_utc = tomorrow_local.astimezone(pytz.UTC).replace(tzinfo=None)
        month_start_utc = month_start_local.astimezone(pytz.UTC).replace(tzinfo=None)

        companies = self.env['res.company'].sudo().search([
            ('company_registry', 'in', COMPANY_REGISTRIES)])

        # Today's occupancy per company: first session (by start_at) that has a non-zero value
        today_sessions = self.env['pos.session'].sudo().search([
            ('config_id.company_id', 'in', companies.ids),
            ('start_at', '>=', today_start_utc),
            ('start_at', '<', tomorrow_start_utc),
        ], order='start_at asc')
        per_company = {}
        for session in today_sessions:
            company_id = session.config_id.company_id.id
            if company_id in per_company:
                continue
            value = session.occupancy_percentage or 0.0
            if value <= 0:
                continue
            per_company[company_id] = round(value, 2)

        company_id_by_name = {c.name: c.id for c in companies}
        for entry in result.get('today_sales_data', []):
            company_id = company_id_by_name.get(entry.get('company'))
            entry['occupancy_percentage'] = per_company.get(company_id, 0.0)

        # Month average: one value per (company, day), latest non-zero kept
        month_sessions = self.env['pos.session'].sudo().search([
            ('config_id.company_id', 'in', companies.ids),
            ('start_at', '>=', month_start_utc),
        ], order='start_at desc')
        values_per_day = {}
        for session in month_sessions:
            value = session.occupancy_percentage or 0.0
            if value <= 0 or not session.start_at:
                continue
            start_local = pytz.UTC.localize(session.start_at).astimezone(tz)
            key = (session.config_id.company_id.id, start_local.date())
            if key in values_per_day:
                continue
            values_per_day[key] = value
        month_values = list(values_per_day.values())
        result['month_avg_occupancy'] = round(sum(month_values) / len(month_values), 2) if month_values else 0.0

        return result
