__author__ = 'Raquel'
# Go through a CINERGI catalog and ensure all links work

from urllib.request import urlopen
from urllib.parse import urljoin
from datetime import datetime
from time import clock
import re

from bs4 import BeautifulSoup

from check_link import check_link
from Catalog_fixer.find_details import find_abstract, find_brief_desc, find_org, find_parent
from field_checks import are_same, tag_in_title
from issues import BadUrl, TitleProb, SuckyDesc


# TODO: Check for duplicate links

NO_LINK = 'No link'
BROKEN_LINK = 'BROKEN LINK'
BD_ABSTRACT_SAME = 'Brief Description and Abstract are the same'
ONLY_ACRONYM = 'Only acronym in title'
LOWERCASE = 'Title is lowercase'
NO_BD = 'No Brief Description'
NO_ABS = 'No Abstract'
NO_SOURCE = 'Abstract missing source'
DUPLICATE_LINK = 'Duplicate link'

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
                 'NOAA National Oceanographic Data Center (NODC) Granule-level Geoportal Server',
                 'NOAA National Oceanographic Data Center (NODC) Granule-level Geoportal Server']

# Orgs whose Brief Descriptions and Abstracts are often the same because of general lack of detail
nondescriptOrgs = ['Rolling Deck to Repository (R2R)', 'Marine Metadata Initative']

# Url for making queries to hydro10
base_url = 'http://hydro10.sdsc.edu/'

# Resource catalog page to start analysis from
start_url = 'http://hydro10.sdsc.edu/HLIResources/Resources'


class Resource:
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
    briefDesc = ""
    abstract = ""
    resourceCategory = ""
    primaryDomain = ""
    domains = []
    communities = []
    gets_pass = False

soup = BeautifulSoup(urlopen(start_url).read())
current_page = soup.find('div', {'class': 'pagination'}).find('li', {'class': 'active'})
page_num = current_page.find('a').text

resources = []
start_time = clock()
print("Analyzing catalog...")
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
        if link_tag.has_attr('href'):
            res_url = link_tag['href']
            status = check_link(res_url)
            if status is not "working" and BROKEN_LINK not in res_title:
                url_prob = BadUrl(status)
                temp_issues.append(url_prob)
        else:
            res_url = 'None'
            url_prob = BadUrl(NO_LINK)
            temp_issues.append(url_prob)
        # Access detail page to get brief description, abstract, org and parent resource
        details = a_resource.find('td', {'class': 'resActions'}).find('div').find('a')
        link_to_details = details['href']
        full_details = urljoin(base_url, link_to_details)
        details_page = BeautifulSoup(urlopen(full_details).read())
        res_briefDesc = find_brief_desc(details_page)
        res_abstract = find_abstract(details_page)
        res_org = find_org(details_page)
        res_parentResource = find_parent(details_page)
        res = Resource(res_title, page_num, res_url, res_org, res_parentResource)
        res.briefDesc = res_briefDesc
        res.abstract = res_abstract
        if all(c.isupper() for c in res.title):
            if not res.gets_pass:
                title_prob = TitleProb(ONLY_ACRONYM)
                temp_issues.append(title_prob)
        first_letter = res.title[0]
        if first_letter.islower():
            title_prob = TitleProb(LOWERCASE)
            temp_issues.append(TitleProb(LOWERCASE))
        # Check if resource is missing Brief Description
        if res.briefDesc is "":
            desc_prob = SuckyDesc(NO_BD)
            temp_issues.append(desc_prob)
        # Check if abstract is insufficient
        if len(re.findall('\w+', res.abstract)) < 2:
            desc_prob = SuckyDesc(NO_ABS)
            temp_issues.append(desc_prob)
        else:
            # If abstract is sufficient, check if abstract is missing source
            if re.search('\(Source: (.*)\)', res.abstract) is None:
                desc_prob = SuckyDesc(NO_SOURCE)
                temp_issues.append(desc_prob)
            # Check if brief desc. and abstract are the same
            if are_same(res.briefDesc, res.abstract):
                if not res.gets_pass:
                    desc_prob = SuckyDesc(BD_ABSTRACT_SAME)
                    temp_issues.append(desc_prob)
        res.issue_space = temp_issues
        if len(res.issue_space) > 0:
            res.has_issues = True
        resources.append(res)

    next_page = current_page.find_next('li').find('a')
    full_url = urljoin(base_url, next_page['href'])
    soup = BeautifulSoup(urlopen(full_url).read())
    current_page = soup.find('div', {'class': 'pagination'}).find('li', {'class': 'active'})
    page_num = current_page.find('a').text

end_time = clock() - start_time
print('Process took {}'.format(end_time))

# List of resources with discernible issues
resources_with_issues = []

issue_counter = 0
for resource in resources:
    if resource.has_issues and tag_in_title(resource.title) is None:
        for i in resource.issue_space:
            issue_counter += 1
        resources_with_issues.append(resource)

# Shuffle resources with issues so ones with highest severity are first
print('Shuffling 2\'s...')
for r in resources_with_issues:
    if any(i.severity is 2 for i in r.issue_space):
        r.severity = 2
        temp = resources_with_issues.pop(resources_with_issues.index(r))
        resources_with_issues.insert(0, temp)

print('Shuffling 3\'s...')
for r in resources_with_issues:
    if any(i.severity is 3 for i in r.issue_space):
        r.severity = 3
        temp = resources_with_issues.pop(resources_with_issues.index(r))
        resources_with_issues.insert(0, temp)

print('Creating output...')
time_created = datetime.now().strftime('%b %d %Y_%I.%m %p')
f = open('Output/HLI Issues_{}.txt.'.format(time_created), 'w+')
f.write('{} total Resources with Issues\n'.format(len(resources_with_issues)))
f.write('{} total issues\n'.format(issue_counter))
for res in resources_with_issues:
    resource = resources_with_issues.pop(0)
    f.write('{}\n pg. {}\n{}\n'.format(resource.title, resource.pg_num, resource.url))
    for each in resource.issue_space:
        f.write("   * {}\n".format(each.issue))
    f.write('\n')

f.close()
print('Done.')
print('{} total Resources with Issues'.format(len(resources_with_issues)))
print('{} total issues'.format(issue_counter))