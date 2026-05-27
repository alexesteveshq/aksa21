# -*- coding: utf-8 -*-

# Bank accounts created (by sales_dashboard) for the POS payment methods
# Banamex MXN/USD, Leisure Cash USD and Kapital MXN/USD (codes
# 109.01.08 .. 109.01.12) must be included in the legacy Profit & Loss report.
# Flagging them here keeps the legacy-report concern in this module.
LEGACY_ACCOUNT_CODES = (
    '109.01.08', '109.01.09', '109.01.10', '109.01.11', '109.01.12',
)


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_account
        SET legacy_report = TRUE
        WHERE code IN %s
          AND COALESCE(legacy_report, FALSE) = FALSE
        """,
        (LEGACY_ACCOUNT_CODES,),
    )
