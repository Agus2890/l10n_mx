# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'City',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',    
    'category': 'Localization/México',
    'description': """
This module creates the city model similar to states model and adds the field city_id on res partner.
    """,
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
            'base', 'contacts',
        ],
    'demo': [],
    'data': [
        'views/res_city_view.xml',
        'views/res_partner_view.xml',
        'security/city_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'active': False,
}

