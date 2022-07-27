# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Crea la aplicación para los grupos de la Factura Electronica',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description': """
Create the application with the groups: User y Manager.
This application is for Electronic Invoice of México
    """,
    'website': 'http://mikrointeracciones.com.mx',    
    'license': 'AGPL-3',
    'depends': ['base'],
    'demo': [],
    'test': [],
    'data': [
        'security/l10n_mx_facturae_security_groups.xml',
        'views/res_config_view.xml'
    ],
    'images': [],
    'application': False,
    'active': False,
    'installable': True,
}
