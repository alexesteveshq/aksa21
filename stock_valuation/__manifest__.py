# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Valuation',
    'summary': 'Increases cost of stock by percentage',
    'description': 'Increases cost of stock by percentage',
    'category': 'Stock',
    'author': 'Visionee',
    'version': '16.0.0.0',
    'depends': [
        'stock_ext',
    ],
    'data': [
        'data/ir_actions.xml',
        'security/ir.model.access.csv',
        'wizard/stock_valuation_update_wizard_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
