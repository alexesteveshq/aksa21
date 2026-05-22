# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz

from odoo import api, models


COMPANY_REGISTRIES = ['sian_kaan', 'dreams_vista', 'grand_outlet', 'costa_mujeres', 'aventuras']


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
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

        # Period for company sales table: honor user-selected range, else current month
        if usr_start_date:
            period_start_utc = datetime.strptime(usr_start_date, '%Y-%m-%d')
        else:
            period_start_utc = month_start_utc
        if usr_end_date:
            period_end_utc = datetime.strptime(usr_end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            period_end_utc = tomorrow_start_utc

        period_sessions = self.env['pos.session'].sudo().search([
            ('config_id.company_id', 'in', companies.ids),
            ('start_at', '>=', period_start_utc),
            ('start_at', '<', period_end_utc),
        ], order='start_at desc')

        # one (company, day) value kept (latest non-zero)
        values_per_day = {}
        for session in period_sessions:
            value = session.occupancy_percentage or 0.0
            if value <= 0 or not session.start_at:
                continue
            start_local = pytz.UTC.localize(session.start_at).astimezone(tz)
            key = (session.config_id.company_id.id, start_local.date())
            if key in values_per_day:
                continue
            values_per_day[key] = value

        # Per-company average across days in the period
        per_company_days = {}
        for (company_id, _date), value in values_per_day.items():
            per_company_days.setdefault(company_id, []).append(value)
        per_company_avg = {
            cid: round(sum(vals) / len(vals), 2) for cid, vals in per_company_days.items()
        }
        for entry in result.get('daily_sales', []):
            company_id = company_id_by_name.get(entry.get('company'))
            entry['occupancy_percentage'] = per_company_avg.get(company_id, 0.0)

        # Overall month avg (across all companies/days in the period)
        all_values = list(values_per_day.values())
        result['month_avg_occupancy'] = round(sum(all_values) / len(all_values), 2) if all_values else 0.0

        return result
