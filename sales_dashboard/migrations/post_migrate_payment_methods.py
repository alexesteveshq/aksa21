# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    target_registries = ['sian_kaan', 'dreams_vista', 'grand_outlet', 'costa_mujeres', 'aventuras']
    companies = env['res.company'].search([('company_registry', 'in', target_registries)])

    usd = env.ref('base.USD')
    mxn = env['res.currency'].search([('name', '=', 'MXN')], limit=1)

    new_methods = [
        {
            'code': 'BANM',
            'journal_name': 'Banamex MXN (Ventas)',
            'pm_name': 'Banamex MXN',
            'account_code': '109.01.08',
            'account_name': 'Banamex MXN',
            'currency': False,
        },
        {
            'code': 'BANU',
            'journal_name': 'Banamex USD (Ventas)',
            'pm_name': 'Banamex USD',
            'account_code': '109.01.09',
            'account_name': 'Banamex USD',
            'currency': usd,
        },
        {
            'code': 'LUSD',
            'journal_name': 'Efectivo USD Leisure (Ventas)',
            'pm_name': 'Leisure Cash USD',
            'account_code': '109.01.10',
            'account_name': 'Efectivo USD Leisure',
            'currency': usd,
        },
        {
            'code': 'KAPM',
            'journal_name': 'Kapital MXN (Ventas)',
            'pm_name': 'Kapital MXN',
            'account_code': '109.01.11',
            'account_name': 'Kapital MXN',
            'currency': False,
        },
        {
            'code': 'KAPU',
            'journal_name': 'Kapital USD (Ventas)',
            'pm_name': 'Kapital USD',
            'account_code': '109.01.12',
            'account_name': 'Kapital USD',
            'currency': usd,
        },
    ]

    for company in companies:
        for method in new_methods:
            # Account currency: USD methods use USD, MXN methods use MXN. The legacy
            # chart sets currency_id even on company-currency (MXN) accounts, and the
            # legacy report groups the parent total by a.currency_id, so it must be set
            # or the parent row sums to 0 while the per-company breakdown shows a value.
            account_currency = method['currency'] or mxn

            # --- Account (find or create) ---
            account = env['account.account'].search([
                ('code', '=', method['account_code']),
                ('company_id', '=', company.id),
            ], limit=1)
            if not account:
                account = env['account.account'].create({
                    'code': method['account_code'],
                    'name': method['account_name'],
                    'account_type': 'asset_cash',
                    'company_id': company.id,
                    'currency_id': account_currency.id if account_currency else False,
                })
            elif not account.currency_id and account_currency:
                # Backfill currency on accounts created before this fix
                cr.execute(
                    "UPDATE account_account SET currency_id = %s WHERE id = %s",
                    (account_currency.id, account.id))

            # --- Journal (find or create) ---
            journal = env['account.journal'].search([
                ('code', '=', method['code']),
                ('company_id', '=', company.id),
            ], limit=1)
            if not journal:
                journal_vals = {
                    'name': method['journal_name'],
                    'code': method['code'],
                    'type': 'bank',
                    'company_id': company.id,
                    'default_account_id': account.id,
                }
                if method['currency']:
                    journal_vals['currency_id'] = method['currency'].id
                journal = env['account.journal'].create(journal_vals)

            # --- POS payment method (find or create) ---
            # outstanding_account_id (Intermediary Account) must point to the bank
            # account so the combined POS closing entry lands on it; otherwise POS
            # falls back to the company's generic Outstanding Receipts account and
            # the amount never reaches this account in the legacy report.
            payment_method = env['pos.payment.method'].search([
                ('journal_id', '=', journal.id),
                ('company_id', '=', company.id),
            ], limit=1)
            if not payment_method:
                payment_method = env['pos.payment.method'].create({
                    'name': method['pm_name'],
                    'journal_id': journal.id,
                    'company_id': company.id,
                    'outstanding_account_id': account.id,
                })
            elif not payment_method.outstanding_account_id:
                payment_method.outstanding_account_id = account.id

            # --- Link the payment method to every active POS of the company ---
            # Write straight to the m2m table: pos.config.write() refuses to touch
            # payment_method_ids while a POS session is open, but for a migration we
            # just need the method available going forward.
            configs = env['pos.config'].search([('company_id', '=', company.id)])
            for config in configs:
                cr.execute(
                    """
                    INSERT INTO pos_config_pos_payment_method_rel
                        (pos_config_id, pos_payment_method_id)
                    SELECT %(config)s, %(pm)s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM pos_config_pos_payment_method_rel
                        WHERE pos_config_id = %(config)s
                          AND pos_payment_method_id = %(pm)s
                    )
                    """,
                    {'config': config.id, 'pm': payment_method.id},
                )
