# -*- encoding: utf-8 -*-
# © 2013 Mikrointeracciones de México (contacto@mikrointeracciones.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom


def AddNode(node_name, attrs, parent_node, minidom_xml_obj, attrs_types, order=False):
        if not order:
            order = attrs
        new_node = minidom_xml_obj.createElement(node_name)
        #new_node = '%s\n' %str(new_node)
        for key in order:
            if attrs_types[key] == 'attribute':
                #new_node.setAttribute(key, '%s\n' %str(attrs[key]))
                new_node.setAttribute(key, attrs[key])
            elif attrs_types[key] == 'textNode':
                key_node = minidom_xml_obj.createElement(key)
                text_node = minidom_xml_obj.createTextNode(attrs[key])
                key_node.appendChild(text_node)
                new_node.appendChild(key_node)
            elif attrs_types[key] == 'att_text':
                new_node.setAttribute('name', key)
                text_node = minidom_xml_obj.createTextNode(attrs[key])
                new_node.appendChild(text_node)
        parent_node.appendChild(new_node)
        return new_node
