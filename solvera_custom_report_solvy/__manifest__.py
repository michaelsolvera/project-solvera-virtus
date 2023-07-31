# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Report Solvy',
    'category': 'Reports',
    'author': 'Michael',
    'version': '1.0',
    'website': 'http://www.solvera.id/',
    'description': """
       solvy Custom Report
    """,
    'data': [
        # 'security/ir.model.access.csv',
        'reports/reports.xml',
        'reports/solvy_invoice.xml',
        'views/invoice_view.xml',

    ],
    "depends": [
        "sale","account"
    ],
    'installable': True,
    "images":['static/logo.png'],
}
