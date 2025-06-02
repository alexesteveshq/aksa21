# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Reports Legacy',
    'summary': 'Account Report Legacy',
    'description': 'Account Report Legacy',
    'author': 'Alex Esteves',
    'depends': [
        'account_reports',
    ],
    'data': [
        'data/account_reports_legacy_data.xml',
        'views/account_account_views.xml',
        'views/account_journal_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
