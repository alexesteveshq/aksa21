# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Aksa',
    'summary': 'Purchase module extension for Aksa',
    'description': 'Purchase module extension for Aksa',
    'category': 'Purchase',
    'author': 'Alex Esteves',
    'depends': [
        'purchase',
        'stock_ext',
    ],
    'data': [
        'views/purchase_views.xml',
        'data/purchase_aksa_data.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
