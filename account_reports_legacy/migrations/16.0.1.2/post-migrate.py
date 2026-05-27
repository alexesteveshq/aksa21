# -*- coding: utf-8 -*-
# Re-run the flag now that sales_dashboard creates the Kapital accounts; the
# 16.0.1.1 run happened before those accounts existed.
from odoo.addons.account_reports_legacy.migrations.flag_legacy_accounts import migrate
