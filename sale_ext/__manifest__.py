# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Extend',
    'summary': 'Sale module extension',
    'description': 'Sale module extension',
    'category': 'Sale',
    'author': 'Alex Esteves',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_ext/static/src/**/*',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
