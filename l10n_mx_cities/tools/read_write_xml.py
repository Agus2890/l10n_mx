# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import xml.dom.minidom
import xml.etree.cElementTree as ET
import os
from add_node import AddNode

data_path = '../data'
source_path = '../source'
file_source = 'l10n_mx_cities.xml'

source_full_path = os.path.join(source_path, file_source)

parser_states_codes = {
    '01': 'ags', '02': 'bc', '03': 'bcs', '04': 'camp', '05': 'coah',
    '06': 'col', '07': 'chis', '08': 'chih', '09': 'df', '10': 'dgo',
    '11': 'gto', '12': 'gro', '13': 'hgo', '14': 'jal', '15': 'mex',
    '16': 'mich', '17': 'mor', '18': 'nay', '19': 'nl', '20': 'oax',
    '21': 'pue', '22': 'qro', '23': 'q roo', '24': 'slp', '25': 'sin',
    '26': 'son', '27': 'tab', '28': 'tamps', '29': 'tlax', '30': 'ver',
    '31': 'yuc', '32': 'zac'}

tree = ET.ElementTree(file=source_full_path)
root = tree.getroot()

cities = []
xml_doc = xml.dom.minidom.Document()
odoo_node = xml_doc.createElement('odoo')
xml_doc.appendChild(odoo_node)
nodeodoo = xml_doc.getElementsByTagName('odoo')[0]
main_node = AddNode('data', {"noupdate": "True"}, nodeodoo,
                    xml_doc, attrs_types={"noupdate": "attribute"})

for elem in root[1:]:
    for a in elem:
        if a.tag == '{NewDataSet}c_mnpio':
            city_code = a.text and a.text or ''
        if a.tag == '{NewDataSet}D_mnpio':
            city = a.text and a.text or ''
        if a.tag == '{NewDataSet}d_estado':
            state = a.text and a.text or ''
        if a.tag == '{NewDataSet}c_estado':
            state_code = a.text and a.text or ''
    city_state = city_code+state_code
    if city_state not in cities:
        cities.append(city_state)
        city_id = 'res_country_state_city_mx_'+state_code+'_'+city_code
        node_record = AddNode('record', {"id": city_id,
                                "model": "res.country.state.city"}, main_node,
                                xml_doc, attrs_types={"id": "attribute",
                                "model": "attribute"})
        main_node.appendChild(node_record)
        node_record_attrs = {
            "name": "country_id",
            "ref": "base.mx",
        }
        node_record_attrs_types = {
            "name": 'attribute',
            "ref": 'attribute',
        }
        order = ['name', 'ref', ]

        node_field = AddNode('field', node_record_attrs, node_record, xml_doc,
                            node_record_attrs_types, order)
        node_record.appendChild(node_field)

        node_city_attrs = {"name": city, }
        node_city_attrs_types = {"name": 'att_text', }
        order = ['name']
        node_field_city = AddNode('field', node_city_attrs, node_record,
                            xml_doc, node_city_attrs_types, order)
        node_record.appendChild(node_field_city)

        node_city_code_attrs = {"code": city_code, }
        node_city_code_attrs_types = {"code": 'att_text', }
        order = ['code']
        node_field_city_code = AddNode('field', node_city_code_attrs,
                    node_record, xml_doc, node_city_code_attrs_types, order)
        node_record.appendChild(node_field_city_code)

        xml_id_states = 'base.state_mx_' + \
            parser_states_codes.get(state_code, '')
        node_states_attrs = {"name": 'state_id', 'ref': xml_id_states}
        node_states_attrs_types = {"name": 'attribute', "ref": "attribute", }
        order = ['name', 'ref']
        node_field_states = AddNode('field', node_states_attrs, node_record,
                                    xml_doc, node_states_attrs_types, order)
        node_record.appendChild(node_field_states)

data_full_path = os.path.join(data_path, 'l10n_mx_cities.xml')

f = open(data_full_path, 'wb')
#f.write(xml_doc.toxml('UTF-8'))
f.write(xml_doc.toprettyxml(indent="\t", encoding="utf-8"))
f.close
