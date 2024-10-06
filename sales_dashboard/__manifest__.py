{
    'name': 'Sales Dashboard',
    'summary': 'Enhanced point of sale dashboard using Owl',
    'description': 'Enhanced point of sale dashboard using Owl framework',
    'category': 'Point of Sale',
    'author': 'Alex Esteves',
    'version': '1.0',
    'depends': ['point_of_sale', 'web', 'pos_sellers'],
    'data': [
        'views/sales_dashboard_menu.xml',  # Menu and action definitions
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js',
            'sales_dashboard/static/src/css/sales_dashboard.css',
            'sales_dashboard/static/src/js/sales_dashboard.js',  # Correct path for the JS file
            'sales_dashboard/static/src/xml/sales_dashboard_view.xml',  # Correct path for the XML file
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
