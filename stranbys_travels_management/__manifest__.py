# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
#   STRANBYS.COM                                                        #
#                                              #
#   GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3)                         #
#                                                                       #
#########################################################################

{
    "name": "Travels Management",
    "description": """This app provides a complete solution for managing travel and expenses for your employees.""",
    "version": "14.0.0.0.0",
    'author': 'Stranbys Info Solutions',
    'company': 'Stranbys Info Solutions',
    'maintainer': 'Stranbys Info Solutions',
    'website': "https://www.stranbys.com",
    "depends": ['base', 'account', 'contacts'],
    "data": [
        'security/ir.model.access.csv',
        'security/travels_security.xml',

        'views/invoice.xml',
        'views/master.xml',
        'views/menus.xml',
        'reports/invoice_report.xml',
        'reports/report_menu.xml',
        

    ],
    'images': ['static/description/banner.png',],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
