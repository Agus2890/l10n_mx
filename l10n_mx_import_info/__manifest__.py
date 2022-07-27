# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Customs Information on lots',
    'version': '1.0',
    'author': 'Vauxoo, OpenPyme, Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
Lots on import products
=================================

Make relation between information of import with government.
With this module you will be able to make a relation between invoice and
Information of importing transaction.
It will work as production lot make better control with quantities.
    """,
    'website': 'www.mikrointeracciones.com.mx',    
    'depends': [
        'product',
        'stock',
        'purchase',
        #'account'
    ],
    'demo': [
        'demo/import_info_demo.xml',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/import_info_view.xml',
        'views/product_view.xml',
        'views/stock_view.xml',
        #'views/label_report.xml',
        #'views/security/groups.xml',
        'views/account_invoice_view.xml',
    ],
    'active': False,
    'installable': True
}
