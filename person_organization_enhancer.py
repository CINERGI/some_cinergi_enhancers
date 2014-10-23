__author__ = 'Raquel'

import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.parse
import re

"""
# Code for eventual working with json
import json
json_file = open('json_metadata/USGINMetadataJSONschemav2')
data = json.load(json_file)

org = data['definitions']['jmd:RelatedAgentObject']['anyOf']['jmd:organizationName']
org_URI = data['definitions']['jmd:RelatedAgentObject']['jmd:organizationURI']
org_links = data['definitions']['jmd:RelatedAgentObject']['jmd:organizationLinks']
"""

# Present library of congress search page
loc_url = 'http://id.loc.gov/search/'

# NCDC resource
# http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/23759C9A-F801-495B-B140-9A41637E3D7C.xml
# CZO resource
# http://hydro10.sdsc.edu/metadata/Critical_Zone_Observatory_Catalog/159C0A40-C9AC-4161-914B-193FBAC9C1D1.xml

tree = ET.parse(urlopen('http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/'
                        '23759C9A-F801-495B-B140-9A41637E3D7C.xml'))
root = tree.getroot()

# find two elements with Responsible Party: contact and identification info
contact = root.find('{http://www.isotc211.org/2005/gmd}contact')
idInfo = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo').find('{http://www.isotc211.org/2005/gmd}'
                                                                                'MD_DataIdentification')

# Elements with organizations
org_elements = []

# in contact, CI_ResponsibleParty is direct child
# Access this child then access the organisationName, characterString and text
contact_orgs = contact.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty').find(
    '{http://www.isotc211.org/2005/gmd}'
    'organisationName').find('{http://www.isotc211.org/2005/gco}CharacterString')
org_elements.append(contact_orgs)

# in idInfo, CI_ResponsibleParty is part of citation and pointOfContact
citation = idInfo.find('{http://www.isotc211.org/2005/gmd}citation').find('{http://www.isotc211.org/2005/gmd}'
                                                                          'CI_Citation')

citation_orgs = citation.find('{http://www.isotc211.org/2005/gmd}citedResponsibleParty').find(
    '{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty').find('{http://www.isotc211.org/2005/gmd}'
                                                                  'organisationName').find('{http://www.isotc211.org/'
                                                                                           '2005/gco}CharacterString')

org_elements.append(citation_orgs)

pointOfContact_orgs = idInfo.find('{http://www.isotc211.org/2005/gmd}pointOfContact'). \
    find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty').find('{http://www.isotc211.org/'
                                                                       '2005/gmd}organisationName').find(
    '{http://www.isotc211.org/2005/gco}CharacterString')
org_elements.append(citation_orgs)

# List to hold strings of organization names
orgs = []

for each in org_elements:
    orgs.extend(re.split('[^a-zA-Z\s\d:.]', each.text))

# Remove duplicates
orgs = list(set(orgs))

# Remove whitespaces
for org in orgs:
    if re.match('(^\s|\s$)', org):
        index = orgs.index(org)
        org_with_spaces = orgs.pop(index)
        # remove spaces from org
        new_org = org_with_spaces.rstrip().lstrip()
        orgs.insert(index, new_org)

print(orgs)
# Send each in a makeshift post request to Library of Congress db of authority names
# Problem: Query uses the same name ('q') for the keyword as well as the options
# for what to search. This is solved by encoding and adding to the url twice
for each in orgs:
    # First attach query to search org name
    term_data = {'q': each}
    term = urllib.parse.urlencode(term_data)
    url_w_name = loc_url + '?' + term
    # Next attach query to search name authority
    options_data = {'q': 'cs:http://id.loc.gov/authorities/names'}
    options = urllib.parse.urlencode(options_data)
    full_url = url_w_name + '&' + options
    the_page = BeautifulSoup(urlopen(full_url).read()).prettify()
    f = open('output_{}.txt'.format(each), 'w+')
    f.write(the_page)
    f.close()