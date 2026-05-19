{
    'name': 'POS Occupancy',
    'summary': 'Register occupancy percentage per POS session',
    'description': 'Adds occupancy_percentage to pos.session, a POS UI button to set it,'
                   ' and integrates the data into the Sales Dashboard.',
    'category': 'Point of Sale',
    'author': 'Alex Esteves',
    'version': '1.0',
    'depends': ['point_of_sale', 'sales_dashboard'],
    'data': [
        'views/pos_session_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_occupancy/static/src/scss/occupancy_button.scss',
            'pos_occupancy/static/src/js/OccupancyButton.js',
            'pos_occupancy/static/src/xml/OccupancyButton.xml',
            'pos_occupancy/static/src/xml/Chrome.xml',
        ],
        'web.assets_backend': [
            'pos_occupancy/static/src/js/sales_dashboard_patch.js',
            'pos_occupancy/static/src/xml/sales_dashboard_view.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
}
