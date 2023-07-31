# -*- coding: utf-8 -*-
{
    'name': "Loans",

    'summary': 'Loan Management System For Microfinance in Africa',
    
    'description': """
        Long description of module's purpose
    """,

    'author': "Emmanuel Lawton",
    'company': "Wakanda Technologies Co.Ltd",
    'website': "#",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Finance',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/loan_mgt.xml',
        'views/borrower_mgt.xml',
        'views/payments.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,

}
