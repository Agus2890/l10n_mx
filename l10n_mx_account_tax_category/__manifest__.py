# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Add category to taxes',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',    
    'category': 'Localization/México',
    'description' : """
This module add to the taxes category & tax_percent
    """,
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',    
    'depends': ['account'],
    'demo' : [],
    'test': [],   
    'data' : [
        'security/ir.model.access.csv',
        # 'views/account_invoice_view.xml',
        'views/account_tax_category_view.xml',
        'data/account_tax_category_data.xml',
    ],
    'active': False,
    'installable': True,
}

