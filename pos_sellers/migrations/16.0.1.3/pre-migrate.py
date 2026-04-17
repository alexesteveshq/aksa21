# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        ALTER TABLE res_partner
            ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS admin_commission_rate DOUBLE PRECISION DEFAULT 0.0;
    """)
