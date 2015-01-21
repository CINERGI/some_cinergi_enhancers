__author__ = 'Raquel'
import xml.etree.ElementTree as ET
import xml.dom.minidom
from parse_xml import parse_xml
from enhance_xml import enhance_xml
from urllib.request import urlopen


def process_xml(filename):
    # List organization names found in document
    orgs = []
    tree = ET.parse(urlopen(filename))
    root = tree.getroot()
    if parse_xml(root, orgs):
        newIDInfo = enhance_xml(root, orgs)
        oldIDInfo = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo')
        index = list(root).index(oldIDInfo)
        root.remove(oldIDInfo)
        root.insert(index, newIDInfo)
        rough_string = ET.tostring(root, 'utf-8')
        parsed = xml.dom.minidom.parseString(rough_string)
        print(parsed.toprettyxml('\t'))
        f = open('enhanced.xml', 'wb+')
        f.write(rough_string)
        f.close()
    else:
        print('Problem reading file')


file = input('Enter the name of a file you wish to enhance: ')
if file.endswith('.xml'):
    namespaces = {'gmi': "http://www.isotc211.org/2005/gmi", 'gmd': "http://www.isotc211.org/2005/gmd", 'gco':
                  "http://www.isotc211.org/2005/gco", 'gml': "http://www.opengis.net/gml/3.2", 'gmx':
                  "http://www.isotc211.org/2005/gmx", 'gsr': "http://www.isotc211.org/2005/gsr",
                  'gss': "http://www.isotc211.org/2005/gss", 'gts': "http://www.isotc211.org/2005/gts",
                  'xlink': "http://www.w3.org/1999/xlink", 'xsi': "http://www.w3.org/2001/XMLSchema-instance",
                  'saxon': "http://saxon.sf.net/", 'schemaLocation': "http://www.isotc211.org/2005/gmi http://www.ngdc."
                                                                     "noaa.gov/metadata/published/xsd/schema.xsd"}
    for prefix in namespaces:
        ET.register_namespace(prefix, namespaces[prefix])
    process_xml(file)