# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Price Increase',
    'summary': 'Purchase Price Increase',
    'description': 'Purchase Price Increase',
    'category': 'Purchase',
    'author': 'Alex Esteves',
    'depends': [
        'purchase', 'stock_ext',
    ],
    'data': [
        'data/ir_actions.xml',
        'wizard/update_product_price_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
