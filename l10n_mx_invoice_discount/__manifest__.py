# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Add field discount to a partner and wizard apply discount on invoice',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/Mexico',
    'description': """
Add field discount to a partner and discount fields on invoice. It's apply discount in all lines when you press compute taxes button. 
Add discount and motive discount fields on xml(CFD and CFDI)
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': ['l10n_mx_facturae_pac'],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [
        'views/product_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable' : True,
    'active' : False,
}
