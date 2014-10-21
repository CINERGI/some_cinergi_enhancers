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

# Library of Congress Search page
loc_url = 'http://authorities.loc.gov/cgi-bin/Pwebrecon.cgi?'
loc_search_page = 'http://authorities.loc.gov/cgi-bin/Pwebrecon.cgi?DB=local&PAGE=First'

tree = ET.parse(urlopen('http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/23759C9A-F801-495B-B140-9A41637E3D7C.xml'))
root = tree.getroot()

# find responsible party
resp_party = root.find('{http://www.isotc211.org/2005/gmd}contact').find('{http://www.isotc211.org/2005/gmd}'
                                                                        'CI_ResponsibleParty')
# find organisationName field and the value in it
org_field_val = resp_party.find('{http://www.isotc211.org/2005/gmd}organisationName').find('{http://www.isotc211.org/'
                                                                                           '2005/gco}CharacterString').text
orgs = re.split('[^a-zA-Z\s\d:.]', org_field_val)

for org in orgs:
    if re.match('(^\s|\s$)', org):
        index = orgs.index(org)
        org_with_spaces = orgs.pop(index)
        # remove spaces from org
        new_org = org_with_spaces.rstrip().lstrip()
        orgs.insert(index, new_org)

# Grab the PID and SEQ from LOC search page because they don't want me to be successful
search_page = BeautifulSoup(urlopen(loc_search_page).read())
PID = search_page.find('input', {'name': 'PID'})['value']
SEQ = search_page.find('input', {'name': 'SEQ'})['value']
print(PID)
print(SEQ)

# Holds the response pages returned by our requests
pages = []
# Now we have a list of orgs with no whitespaces
for each in orgs:
    values = {'Search_Arg': each,
              'Search_Code': 'NHED_',
              'PID': PID,
              'SEQ': SEQ,
              'CNT': 100,
              'HIST': 1}
    myData = urllib.parse.urlencode(values)
    data = myData.encode('utf-8')
    req = Request(loc_url, data)
    response = urlopen(req)
    the_page = BeautifulSoup(response.read()).prettify()
    pages.append(the_page)

f = open('output.txt', 'r+')
f.write(pages[len(pages)-1])
f.close()