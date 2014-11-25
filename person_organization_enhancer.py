__author__ = 'Raquel'

import xml.etree.ElementTree as ET
import xml.dom.minidom
from Organization import Organization, already_in, pseudo_encode
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
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

# VIAF base url
viaf_base = 'http://viaf.org/viaf/search'

# string for searching corporate names
corporate_names = 'local.corporateNames'

# String for searching all of viaf
all_viaf = 'all'

# Orcid search page
orcid_url = 'https://orcid.org/orcid-search/quick-search'

#def generic_name(search_for, string_found):

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

title = citation.find('{http://www.isotc211.org/2005/gmd}title').find('{http://www.isotc211.org/2005/gco}'
                                                                      'CharacterString').text

citation_rp = citation.find('{http://www.isotc211.org/2005/gmd}citedResponsibleParty')

if citation_rp is not None:
    more_orgs = citation_rp.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty').\
        find('{http://www.isotc211.org/2005/gmd}organisationName').\
        find('{http://www.isotc211.org/2005/gco}CharacterString')
    org_elements.append(more_orgs)

# Find all points of contact
pointsOfContact = idInfo.findall('{http://www.isotc211.org/2005/gmd}pointOfContact')

for each in pointsOfContact:
    orgName = each.find('{http://www.isotc211.org/2005/gmd}'
                        'CI_ResponsibleParty').find('{http://www.isotc211.org/2005/gmd}organisationName')
    if orgName is not None:
        org_elements.append(orgName.find('{http://www.isotc211.org/2005/gco}CharacterString'))


# List to hold strings of organization names
org_names = []

for each in org_elements:
    org_names.extend(re.split('[^a-zA-Z\s\d:.]', each.text))

orgs = []

# Remove whitespaces
for o in org_names:
    if re.match('(^\s|\s$)', o):
        # remove spaces from org
        no_spaces = o.rstrip().lstrip()
        if not already_in(no_spaces, orgs):
            new_org = Organization(no_spaces)
            orgs.append(new_org)
    else:
        if not already_in(o, orgs):
            new_org = Organization(o)
            orgs.append(new_org)

#for o in orgs:
#    print(o.string)

names = []
for p in pointsOfContact:
    ci_respParty = p.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty')
    indiv = ci_respParty.find('{http://www.isotc211.org/2005/gmd}individualName')
    if indiv:
        name = indiv.find('{http://www.isotc211.org/2005/gco}CharacterString').text
        if name not in names:
            names.append(name)

# Send each in a makeshift post request to Library of Congress db of authority names
# Problem: Query uses the same name ('q') for the keyword as well as the options
# for what to search. This is solved by encoding and adding to the url twice

# TODO: Search results for correct result
last = orgs[len(orgs)-2]
string_to_encode = '"' + last.string + '"'
encoded_search_terms = pseudo_encode(string_to_encode)
terms = [corporate_names, all_viaf, encoded_search_terms]
print("Searching for:" + last.string)
query_string = 'query='
for each in terms:
    query_string += each
    if each is not terms[len(terms)-1]:
        query_string += '+'
data = {'recordSchema': 'BriefVIAF',
        'sortKeys': 'holdingscount'}
values = urllib.parse.urlencode(data, 'utf-8')
full_url = viaf_base + '?' + query_string + '&' + values
tree = ET.parse(urlopen(full_url))
root = tree.getroot()
records = root.find('{http://www.loc.gov/zing/srw/}records')
for child in records:
    recordData = child.find('{http://www.loc.gov/zing/srw/}recordData')
    cluster = recordData.find('{http://viaf.org/viaf/terms#}VIAFCluster')
    ctitle = cluster.find('{http://viaf.org/viaf/terms#}mainHeadings').find('{http://viaf.org/viaf/terms#}data').\
        find('{http://viaf.org/viaf/terms#}text')
    # Find a generic match
    if re.search(u'{0:s} \(.*\)$'.format(last.string), str(ctitle.text)) is not None:
        print(ctitle.text)
f = open('post_output.txt', 'wb+')
returned = urlopen(full_url).read()
f.write(returned)
f.close()
f = open('post_output.txt', 'r+')
xml = xml.dom.minidom.parse(f)
pretty_xml_as_string = xml.toprettyxml()
f.write(pretty_xml_as_string)
f.close()



# TODO: Find way to extract names
for each in names:
    search_val = {'keys': each}
    data = urllib.parse.urlencode(search_val)
    myData = data.encode('utf-8')
    req = Request(orcid_url, myData)
    the_page = BeautifulSoup(urlopen(req).read()).prettify()
    f = open('output_{}.text'.format(each), 'w+')
    f.write(the_page)
    f.close()
