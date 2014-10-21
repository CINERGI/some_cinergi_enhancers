__author__ = 'Raquel'

import xml.etree.ElementTree as ET
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

# Present library of congress search page
loc_url = 'http://id.loc.gov/search/'

tree = ET.parse(
    urlopen('http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/23759C9A-F801-495B-B140-9A41637E3D7C.xml'))
root = tree.getroot()

# find responsible party
resp_party = root.find('{http://www.isotc211.org/2005/gmd}contact').find('{http://www.isotc211.org/2005/gmd}'
                                                                         'CI_ResponsibleParty')
# find organisationName field and the value in it
org_field_val = resp_party.find('{http://www.isotc211.org/2005/gmd}'
                                'organisationName').find('{http://www.isotc211.org/2005/gco}CharacterString').text
orgs = re.split('[^a-zA-Z\s\d:.]', org_field_val)

for org in orgs:
    if re.match('(^\s|\s$)', org):
        index = orgs.index(org)
        org_with_spaces = orgs.pop(index)
        # remove spaces from org
        new_org = org_with_spaces.rstrip().lstrip()
        orgs.insert(index, new_org)

# Now we have a list of orgs with no whitespaces
# Remove duplicates
orgs = list(set(orgs))

# Send each in a makeshift post request to Library of Congress db of authority names
# Problem: Query uses the same name ('q') for the keyword as well as the options
#          for what to search. This is solved by encoding and adding to the url twice
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