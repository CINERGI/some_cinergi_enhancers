__author__ = 'Raquel'
import xml.etree.ElementTree as ET
#import xml.dom.minidom
from parse_xml import parse_xml
from enhance_xml import enhance_xml
from urllib.request import urlopen


def main():
    # List organization names found in document
    orgs = []
    file = input('Enter the name of a file you wish to enhance: ')
    namespaces = {'gmi': "http://www.isotc211.org/2005/gmi", 'gmd': "http://www.isotc211.org/2005/gmd", 'gco':
                  "http://www.isotc211.org/2005/gco", 'gml': "http://www.opengis.net/gml/3.2", 'gmx':
                  "http://www.isotc211.org/2005/gmx", 'gsr': "http://www.isotc211.org/2005/gsr",
                  'gss': "http://www.isotc211.org/2005/gss", 'gts': "http://www.isotc211.org/2005/gts",
                  'xlink': "http://www.w3.org/1999/xlink", 'xsi': "http://www.w3.org/2001/XMLSchema-instance",
                  'saxon': "http://saxon.sf.net/", 'srv': "http://www.isotc211.org/2005/srv",
                  'schemaLocation': "http://www.isotc211.org/2005/gmi http://www.ngdc.noaa.gov/metadata/"
                                    "published/xsd/schema.xsd"}
    tree = ET.parse(urlopen(file))
    root = tree.getroot()
    for prefix in namespaces:
        ET.register_namespace(prefix, namespaces[prefix])
    # Read document and populate orgs list with raw organization names found
    if parse_xml(root, orgs):
        if len(orgs) == 0:
            print('No organization names could be found in the document')
            exit()
        enhanced_orgs = []
        for each in orgs:
            if each.validate_in_viaf():
                enhanced_orgs.append(each)
        if len(enhanced_orgs) == 0:
            print('No enhancements were made')
            exit()
        # Enhance xml document
        enhance_xml(root, enhanced_orgs)
        rough_string = ET.tostring(root, 'utf-8')
        #parsed = xml.dom.minidom.parseString(rough_string)
        #print(parsed.toprettyxml('\t'))
        f = open('enhanced.xml', 'wb+')
        f.write(rough_string)
        f.close()
    else:
        print('Problem reading document')

main()