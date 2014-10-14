__author__ = 'Raquel'

"""
# Code for eventual working with json
import json
json_file = open('json_metadata/USGINMetadataJSONschemav2')
data = json.load(json_file)

org = data['definitions']['jmd:RelatedAgentObject']['anyOf']['jmd:organizationName']
org_URI = data['definitions']['jmd:RelatedAgentObject']['jmd:organizationURI']
org_links = data['definitions']['jmd:RelatedAgentObject']['jmd:organizationLinks']
"""

import xml.etree.ElementTree as ET
from urllib.request import urlopen

tree = ET.parse(urlopen('http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/23759C9A-F801-495B-B140-9A41637E3D7C.xml'))
root = tree.getroot()

contacts = root.findall('{http://www.isotc211.org/2005/gmd}contact')
orgs = []
for c in contacts:
    org = c.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty')
    orgs.append(org)

total_org_names = []
for o in orgs:
    org_name = o.find('{http://www.isotc211.org/2005/gmd}organisationName').find('{http://www.isotc211.org/2005/gco}'
                                                                                 'CharacterString').text
    total_org_names.append(org_name)

for org_name in total_org_names:
    print(org_name)
