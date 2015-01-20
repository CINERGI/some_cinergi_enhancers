__author__ = 'Raquel'

import xml.etree.ElementTree as ET
from Organization import Organization, already_in
from urllib.request import urlopen
import re

# VIAF base url
viaf_base = 'http://viaf.org/viaf/search'

# string for searching corporate names
corporate_names = 'local.corporateNames'

# String for searching all of viaf
all_viaf = 'all'

# character string
char_string = '{http://www.isotc211.org/2005/gco}CharacterString'

# NCDC resource
# http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/23759C9A-F801-495B-B140-9A41637E3D7C.xml
# CZO resource
# http://hydro10.sdsc.edu/metadata/Critical_Zone_Observatory_Catalog/159C0A40-C9AC-4161-914B-193FBAC9C1D1.xml

tree = ET.parse(urlopen('http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/23759C9A-F801'
                        '-495B-B140-9A41637E3D7C.xml'))
root = tree.getroot()

# find two elements with Responsible Party: contact and identification info
contact = root.find('{http://www.isotc211.org/2005/gmd}contact')
idInfo = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo').find('{http://www.isotc211.org/2005/gmd}'
                                                                                'MD_DataIdentification')

# Dictionary with parent elements as keys
orgs_found = {}

# in contact, CI_ResponsibleParty is direct child
# Access this child then access the organisationName, characterString and text
contact_rp = contact.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty')
contact_orgs = contact_rp.find('{http://www.isotc211.org/2005/gmd}organisationName').\
    find('{http://www.isotc211.org/2005/gco}CharacterString').text
orgs_found[contact_rp] = contact_orgs

# in idInfo, CI_ResponsibleParty is part of citation and pointOfContact
citation = idInfo.find('{http://www.isotc211.org/2005/gmd}citation').find('{http://www.isotc211.org/2005/gmd}'
                                                                          'CI_Citation')

citation_rp = citation.find('{http://www.isotc211.org/2005/gmd}citedResponsibleParty')

if citation_rp is not None:
    more_orgs = citation_rp.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty').\
        find('{http://www.isotc211.org/2005/gmd}organisationName').\
        find('{http://www.isotc211.org/2005/gco}CharacterString').text
    orgs_found[citation_rp] = more_orgs

# Find all points of contact
pointsOfContact = idInfo.findall('{http://www.isotc211.org/2005/gmd}pointOfContact')

for each in pointsOfContact:
    poc_rp = each.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty')
    orgName = poc_rp.find('{http://www.isotc211.org/2005/gmd}organisationName')
    if orgName is not None:
        orgs_found[poc_rp] = orgName.find('{http://www.isotc211.org/2005/gco}CharacterString').text

# List to hold Organization objects
orgs = []

for k in orgs_found:
    orgs_found[k] = re.split('[^a-zA-Z\s\d:.]', orgs_found[k])
    for each in orgs_found[k]:
        if re.match('(^\s|\s$)', each):
            # remove spaces from org
            no_spaces = each.rstrip().lstrip()
            if not already_in(no_spaces, orgs):
                new_org = Organization(no_spaces)
                new_org.parentElem = k
        else:
            if not already_in(each, orgs):
                new_org = Organization(each)
                new_org.parentElem = k


# TODO: spit out enhanced XML doc
# TODO: spit out just the enhancements

# Send each in a makeshift post request to Library of Congress db of authority names
# Problem: Query uses the same name ('q') for the keyword as well as the options
# for what to search. This is solved by encoding and adding to the url twice
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

"""
# Code for people enhancer
names = []
for p in pointsOfContact:
    ci_respParty = p.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty')
    indiv = ci_respParty.find('{http://www.isotc211.org/2005/gmd}individualName')
    if indiv:
        name = indiv.find('{http://www.isotc211.org/2005/gco}CharacterString').text
        if name not in names:
            names.append(name)

for each in names:
    search_val = {'keys': each}
    data = urllib.parse.urlencode(search_val)
    myData = data.encode('utf-8')
    req = Request(orcid_url, myData)
    the_page = BeautifulSoup(urlopen(req).read()).prettify()
    f = open('output_{}.text'.format(each), 'w+')
    f.write(the_page)
    f.close()
"""
