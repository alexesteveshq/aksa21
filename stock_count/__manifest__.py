# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Count',
    'summary': 'Count pieces from stock by scanning them massively',
    'description': 'Count pieces from stock by scanning them massively',
    'category': 'Stock',
    'author': 'Alex Esteves',
    'version': '16.0.0.1',
    'depends': [
        'stock',
    ],
    'data': [
        'data/ir_actions.xml',
        'security/ir.model.access.csv',
        'wizard/stock_count_piece_wizard_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
