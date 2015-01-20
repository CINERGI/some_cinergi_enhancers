__author__ = 'Raquel'

from Organization import Organization, already_in
# Ingest JSON or XML doc

# Code for eventual working with json
import json
json_file = open('json_metadata/USGINMetadataJSONschemav2')
data = json.load(json_file)

orgs = []
org = data['definitions']['jmd:RelatedAgentObject']['anyOf']['jmd:organizationName']
new_org = Organization(org)
orgs.append(new_org)
org_URI = data['definitions']['jmd:RelatedAgentObject']['jmd:organizationURI']
org_links = data['definitions']['jmd:RelatedAgentObject']['jmd:organizationLinks']