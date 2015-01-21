__author__ = 'Raquel'
import xml.etree.ElementTree as ET
import xml.dom.minidom
from parse_xml import parse_xml
from enhance_xml import enhance_xml
from urllib.request import urlopen
import lxml

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
    process_xml(file)

# TODO: spit out enhanced XML doc
# TODO: spit out just the enhancements
"""
f = open('post_output.txt', 'wb+')
returned = urlopen(full_url).read()
f.write(returned)
f.close()
f = open('post_output.txt', 'r+')
xml = xml.dom.minidom.parse(f)
pretty_xml_as_string = xml.toprettyxml()
f.write(pretty_xml_as_string)
f.close()
"""