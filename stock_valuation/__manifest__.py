# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Price Update',
    'summary': 'Increases or decreases the label prices of the pieces in stock by percentage',
    'description': 'Increases or decreases the label prices (USD and MXN) of the pieces in stock by percentage',
    'category': 'Stock',
    'author': 'Visionee',
    'version': '16.0.1.0',
    'depends': [
        'stock_ext',
    ],
    'data': [
        'data/ir_actions.xml',
        'security/ir.model.access.csv',
        'wizard/stock_price_update_wizard_views.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
