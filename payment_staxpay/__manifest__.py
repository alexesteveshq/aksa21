{
    'name': 'StaxPay Payment Integration',
    'version': '16.0',
    'category': 'Accounting/Payment',
    'summary': 'Integrate StaxPay Payment Gateway with Odoo',
    'description': """
        This module integrates the StaxPay payment gateway with Odoo.
    """,
    'author': 'Your Name',
    'depends': ['payment'],
    'assets': {
        'web.assets_frontend': [
            'payment_staxpay/static/src/js/payment_form.js',
            'payment_staxpay/static/src/css/payment_staxpay.css',
        ],
    },
    'data': [
        'views/payment_form_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'installable': True,
    'application': False,
}
