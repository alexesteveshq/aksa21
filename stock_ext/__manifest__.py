# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Inventory Extend',
    'summary': 'Inventory module extension',
    'description': 'Inventory module extension',
    'category': 'Inventory',
    'author': 'Alex Esteves',
    'depends': [
        'account',
        'stock',
        'web_refresher',
    ],
    'data': [
        'data/stock_ext_data.xml',
        'data/ir_actions.xml',
        'views/stock_views.xml',
        'views/piece_variant_views.xml',
        'security/ir.model.access.csv',
        'views/stock_pieces_views.xml',
        'views/stock_quant_views.xml',
    ],
    'external_dependencies': {
        'python': ['zpl'],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
