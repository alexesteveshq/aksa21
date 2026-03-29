# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    target_registries = ['sian_kaan', 'dreams_vista', 'grand_outlet', 'costa_mujeres', 'aventuras']
    companies = env['res.company'].search([('company_registry', 'in', target_registries)])

    usd = env.ref('base.USD')

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
    ]

    for company in companies:
        for method in new_methods:
            # Skip if journal already exists for this company
            existing_journal = env['account.journal'].search([
                ('code', '=', method['code']),
                ('company_id', '=', company.id),
            ], limit=1)
            if existing_journal:
                continue

            # Get or create the GL account
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
                    'currency_id': method['currency'].id if method['currency'] else False,
                })

            # Create the journal
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

            # Create the payment method
            env['pos.payment.method'].create({
                'name': method['pm_name'],
                'journal_id': journal.id,
                'company_id': company.id,
            })
