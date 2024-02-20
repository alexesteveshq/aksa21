# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Aksa',
    'summary': 'Account module extension for Aksa',
    'description': 'Account module extension for Aksa',
    'category': 'Account',
    'author': 'Alex Esteves',
    'depends': [
        'stock_account',
    ],
    'data': [
        'data/ir_actions.xml',
        'views/product_category_views.xml',
        'wizard/update_rate_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
