# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Group For Wizards Of Facturae',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',
    'category': 'Localization/México',
    'description' : """
Group for show wizards of FacturaE
==================================

This module creates the group Show Default Wizards FacturaE, if a user has this group,\n 
can see the facturae wizards, however is advisable that nobody has this group assigned. \n
Wizards to show:\n

- Factura Electronica XML \n
- Cancelar FActura PAC SF \n
- Subir Factura al PAC V6 \n
    """,
    'website': 'www.mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends' : ['base',
    ],
    'demo' : [],
    'data' : [
        'security/res_groups.xml',
    ],
    'installable' : True,
    'active' : False,
}
