# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    "name": "Pos Auto Send Email",
    "version": "15.0.0.0.1",
    'author': "Candidroot Solutions Pvt. Ltd.",
    'website': 'https://www.candidroot.com/',
    'category': 'Point of Sale',
    'description': """ This module allows to send an email when validating PoS order.""",
    "depends": ['base', 'point_of_sale', 'pos_sale'],
    'data': [
        'views/pos_config.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_auto_send_email/static/src/js/send_mail.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://youtu.be/vX_qoSM5vOw',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}