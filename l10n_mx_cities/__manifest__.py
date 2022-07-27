# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mexican Cities',
    'version': '1.0',
    'author': 'Mikrointeracciones de México',    
    'category': 'Localization/México',
    'description': """
This module adds all Mexico's cities based in SEPOMEX

You can download the xml file from http://www.correosdemexico.gob.mx/ServiciosLinea/Paginas/DescargaCP.aspx, save it in source folder with the name 'l10n_mx_cities.xml'
and execute read_write_xml.py file for generate a xml compatible with Odoo in the folder 'data'.
When you install this module, Odoo is going to import the cities from the xml file 'data/l10n_mx_cities.xml'
    """,
    'website': 'http://mikrointeracciones.com.mx',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'city',
    ],
    'data': [
        'data/l10n_mx_cities.xml',
    ],
    'installable': True,
    'active': False,
}



