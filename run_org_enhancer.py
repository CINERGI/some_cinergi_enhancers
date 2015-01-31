__author__ = 'Raquel'
import xml.etree.ElementTree as ET
import xml.dom.minidom
from parse_xml import parse_xml
from enhance_xml import enhance_xml
from urllib.request import urlopen

choice = 'Organization names found. Press (I) to iterate through each organization name found. Press (C) to continue ' \
         'enhancing the document\n'


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
            print('No organization names could be found in the document. Exiting...')
            exit()
        option = input(choice)
        if option == 'I':
            for each in orgs:
                print(each.name)
                next_thing = input('(E)nhance organization or press any other key to continue '
                                   'iterating through organizations found.\n')
                if next_thing == 'E':
                    each.validate_in_viaf()
                    print(each.enhancement_info())
                if next_thing == 'C':
                    continue
        enhanced_orgs = []
        enhance_doc = input('Enhance document? If no, program will exit [Y/N]: ')
        if enhance_doc == 'N':
            exit()
        if enhance_doc == 'Y':
            for each in orgs:
                if each.validated:
                    enhanced_orgs.append(each)
            if len(enhanced_orgs) == 0:
                print('No enhancements could be made. Exiting.')
                exit()
            # Enhance xml document
            enhance_xml(root, enhanced_orgs)
            rough_string = ET.tostring(root, 'utf-8')
            parsed = xml.dom.minidom.parseString(rough_string)
            #print(parsed.toprettyxml('\t'))
            f = open('enhanced.xml', 'wb+')
            f.write(parsed.toxml('utf-8'))
            f.close()
            print('Enhanced document created. See enhanced.xml')
    else:
        print('Problem reading document')

main()