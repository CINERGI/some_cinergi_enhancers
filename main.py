__author__ = 'Raquel'
# Go through a CINERGI catalog and ensure all links work

from urllib.request import urlopen
from urllib.parse import urljoin
from time import time, strftime, localtime
import re
from bs4 import BeautifulSoup
from check_link import check_link
from para_differ import find_abstract, find_brief_desc, are_same
from org_finder import find_org
from issues import BadUrl, TitleProb, SuckyDesc


NO_LINK = 'No link'
BROKEN_LINK = 'BROKEN LINK'
BD_ABSTRACT_SAME = 'Brief Description and Abstract are the same'
ONLY_ACRONYM = 'Only acronym in title'
LOWERCASE = 'Title is lowercase'
NO_BD = 'No Brief Description'
NO_ABS = 'No Abstract'

# Orgs whose Brief Descriptions and Abstracts are often the same because of general lack of detail
nondescriptOrgs = ['Rolling Deck to Repository', 'Marine Metadata Initiative']
base_url = 'http://hydro10.sdsc.edu/'
start_url = 'http://hydro10.sdsc.edu/HLIResources/Resources'

class Resource:
    def __init__(self, res_title):
        self.title = res_title

    url = None
    severity = 0
    pg_num = 0
    has_issues = False
    issue_space = []
    briefDesc = ""
    abstract = ""
    resourceCategory = ""
    primaryDomain = ""
    domains = []
    communities = []
    org = ""


def tagged(res_title):
    return re.search('\((DUPLICATE( [0-9])?|DEPRECATED|BROKEN LINK|LOW REL)\)', res_title)


soup = BeautifulSoup(urlopen(start_url).read())
current_page = soup.find('div', {'class': 'pagination'}).find('li', {'class': 'active'})
page_num = current_page.find('a').text

resources = []
start_time = time()
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
        temp_issues = []
        title = a_resource.find('td', {'class': 'resTitle'}).find('div').text
        res = Resource(title)
        if all(c.isupper() for c in title):
            title_prob = TitleProb(ONLY_ACRONYM)
            temp_issues.append(title_prob)
        first_letter = title[0]
        if first_letter.islower():
            title_prob = TitleProb(LOWERCASE)
            temp_issues.append(TitleProb(LOWERCASE))
        res.pg_num = page_num
        link_tag = a_resource.find('a', text='Link')
        if link_tag.has_attr('href'):
            res.url = link_tag['href']
            status = check_link(res.url)
            if status is not "working" and BROKEN_LINK not in res.title:
                url_prob = BadUrl(status)
                temp_issues.append(url_prob)
        else:
            url_prob = BadUrl(NO_LINK)
            temp_issues.append(url_prob)

        details = a_resource.find('td', {'class': 'resActions'}).find('div').find('a')
        link_to_details = details['href']
        full_details = urljoin(base_url, link_to_details)
        details_page = BeautifulSoup(urlopen(full_details).read())
        res.briefDesc = find_brief_desc(details_page)
        res.abstract = find_abstract(details_page)
        res.org = find_org(details_page)
        if res.briefDesc is "":
            desc_prob = SuckyDesc(NO_BD)
            temp_issues.append(desc_prob)
        if len(re.findall('\w+', res.abstract)) < 2:
            desc_prob = SuckyDesc(NO_ABS)
            temp_issues.append(desc_prob)
        if are_same(res.briefDesc, res.abstract):
            if res.org not in nondescriptOrgs and res.title != res.briefDesc:
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

end_time = time() - start_time
print('Process took {}'.format(end_time))

# List of resources with discernible issues
resources_with_issues = []

for resource in resources:
    if resource.has_issues and tagged(resource.title) is None:
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

issue_res_counter = 0
issue_counter = 0
print('Creating output...')
time_created = strftime('%b %d %Y %I:%m %p', localtime())
f = open('Output/HLI Issues_{}.txt.'.format(time_created), 'w+')
for res in resources_with_issues:
    resource = resources_with_issues.pop(0)
    issue_res_counter += 1
    f.write('{}\n pg. {}\n{}\n'.format(resource.title, resource.pg_num, resource.url))
    for each in resource.issue_space:
        issue_counter += 1
        f.write("   * {}\n".format(each.issue))
    f.write('\n')

f.close()
print('Done.')
print('{} total Resources with Issues'.format(issue_res_counter))
print('{} total issues'.format(issue_counter))