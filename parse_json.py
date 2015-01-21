__author__ = 'Raquel'

# Ingest JSON or XML doc

from Organization import Organization, already_in
import json


json_file = open('json_metadata/USGINMetadataJSONschemav2')
data = json.load(json_file)
