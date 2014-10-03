__author__ = 'Raquel'

import re
from issues import SuckyDesc
from bs4 import BeautifulSoup
from urllib.request import urlopen, urljoin
from find_details import find_abstract, find_org, find_parent
from datetime import datetime

NO_ABS = 'No Abstract'
NO_SOURCE = 'Abstract missing source'

# Resources that get a pass because for having Brief Desc == Abstract or having no source for their abstract
# because the platforms they are hosted on often lack descriptions
passResources = ['USGS Global Data Explorer', 'SAP-DCC Web Feature Service', 'Open Topography find lidar data',
                 'Open Geospatial Consortium (OGC) Feature Web Service', 'USAP-DCC Web Feature Service',
                 'NOAA Index of Snow/Ice related datasets', 'NASA Reverb/ECHO', 'MediaBank',
                 'LSDI' 'Key to TDWG Standards Status and Categories', 'IOOS Controlled Vocabularies Documentation',
                 'MMI Ontology Registry and Repository (ORR)', 'THREDDS', 'LSDI', 'SESAR Collection Method',
                 'SESAR Country List', 'SESAR Material', 'SESAR Metadata Fields', 'SESAR Mineral Classification',
                 'SESAR Navigation Type', 'SESAR Physiographic Feature', 'SESAR Platform Type',
                 'SESAR Rock Classification', 'SESAR Sample Type (Object)', 'SESAR vocabularies',
                 'SESAR web services API documentation', 'SESAR web services schema', 'CIAD OV Services',
                 'Emergency Data Exchange Language (EDXL)', 'CHRONOS', 'ANTARES', 'AGROVOC'
                 'NOAA National Oceanographic Data Center (NODC) Granule-level Geoportal Server']

# Orgs whose Brief Descriptions and Abstracts are often the same because of general lack of detail
nondescriptOrgs = ['Rolling Deck to Repository (R2R)', 'Marine Metadata Initative']

# Url for making queries to hydro10
base_url = 'http://hydro10.sdsc.edu/'

# Resource catalog page to start analysis from
start_url = 'http://hydro10.sdsc.edu/HLIResources/Resources'

class Resource_No_Source:
    def __init__(self, title, pg_num, url, org, parent_resource):
        self.title = title
        self.pg_num = pg_num
        self.url = url
        self.org = org
        self.parentResource = parent_resource
        if self.title in passResources:
            self.gets_pass = True
        if self.org in nondescriptOrgs:
            self.gets_pass = True
        if self.parentResource in passResources:
            self.gets_pass = True
    has_issues = False
    issue_space = []
    abstract = ""
    gets_pass = False
    recommended_source = ""

soup = BeautifulSoup(urlopen(start_url).read())
current_page = soup.find('div', {'class': 'pagination'}).find('li', {'class': 'active'})
page_num = current_page.find('a').text


def build_title(url):
    page_text = BeautifulSoup(urlopen(url).read())
    title = page_text.find('title', text=True)
    if title is not None:
        if title.has_attr('string'):
            return title.string
        else:
            return title.text
    return title

resources = []
while current_page.find_next('li') is not None:
    # Get the table
    table = soup.find('table')

    # Get all rows in the table
    table_rows = table.find_all('tr')

    # Pop off header row
    table_rows.pop(0)

    # Each row in the table is a resource
    for a_resource in table_rows:
        # First gather data to create resource
        temp_issues = []
        # Get title
        res_title = a_resource.find('td', {'class': 'resTitle'}).find('div').text.strip()
        # Get link
        link_tag = a_resource.find('a', text='Link')
        res_url = link_tag['href']
        # Access detail page to get brief description, abstract, org and parent resource
        details = a_resource.find('td', {'class': 'resActions'}).find('div').find('a', text='Details')
        edit = a_resource.find('td', {'class': 'resActions'}).find('div').find('a', text='Edit')
        link_to_edit = edit['href']
        details_page = BeautifulSoup(urlopen(urljoin(base_url, details['href'])).read())
        res_abstract = find_abstract(details_page)
        res_org = find_org(details_page)
        res_parentResource = find_parent(details_page)
        res = Resource_No_Source(res_title, page_num, res_url, res_org, res_parentResource)
        # Check if abstract is insufficient
        if len(re.findall('\w+', res.abstract)) > 2:
            # If abstract is sufficient, check if abstract is missing source
            if re.search('\(Source: (.*)\)', res.abstract) is None:
                resource_page = urlopen(res.url).read()
                if re.search(res.abstract, resource_page) is not None:
                    source_title = resource_page.find('title', text=True)
                    if source_title is not None:
                        res.recommended_source = source_title
                    else:
                        res.recommended_source = 'Could not find good source. Check resource'
        else:
            desc_prob = SuckyDesc(NO_ABS)
            temp_issues.append(desc_prob)

        if len(res.issue_space) > 0:
            res.issue_space = temp_issues
            res.has_issues = True
        resources.append(res)

    next_page = current_page.find_next('li').find('a')
    full_url = urljoin(base_url, next_page['href'])
    soup = BeautifulSoup(urlopen(full_url).read())
    current_page = soup.find('div', {'class': 'pagination'}).find('li', {'class': 'active'})
    page_num = current_page.find('a').text

for r in resources:
    if r.has_issues:
        temp = resources.pop(resources.index(r))
        resources.insert(0, temp)

time_created = datetime.now().strftime('%b %d %Y_%I.%m %p')
f = open('Output/Resources_Abstracts_noSource_{}.txt.'.format(time_created), 'w+')
for res in resources:
    f.write('{}\n pg. {}\n{}\n'.format(res.title, res.pg_num, res.url))
    if res.has_issues:
        for each in res.issue_space:
            f.write("   * {}\n".format(each.issue))
        f.write('\n')
    else:
        f.write(("   * {}\n".format(res.recommended_source)))

f.close()