# -*- coding: utf-8 -*-
# Re-run to backfill outstanding_account_id on payment methods created before
# that fix (otherwise their POS closing entries land on Outstanding Receipts).
from odoo.addons.sales_dashboard.migrations.post_migrate_payment_methods import migrate
