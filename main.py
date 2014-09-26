__author__ = 'Raquel'
# Go through a CINERGI catalog and ensure all links work

from urllib.request import urlopen
from urllib.parse import urljoin
import time
from bs4 import BeautifulSoup
from check_link import check_link
from para_differ import find_abstract, find_brief_desc, are_same


class Resource:
    def __init__(self, res_title):
        self.title = res_title
    url = None
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


def already_tagged(res_title):
    return BROKEN_LINK in res_title

NO_LINK = 'No link'
BROKEN_LINK = 'BROKEN LINK'
BD_ABSTRACT_SAME = 'Brief Description and Abstract are the same'

base_url = 'http://hydro10.sdsc.edu/'
start_url = 'http://hydro10.sdsc.edu/HLIResources/Resources'

soup = BeautifulSoup(urlopen(start_url).read())
current_page = soup.find('div', {'class': 'pagination'}).find('li', {'class': 'active'})
page_num = current_page.find('a').text

resources = []
start_time = time.time()
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
        first_letter = title[0]
        if first_letter.islower():
            temp_issues.append("Title is lowercase")
        res.pg_num = page_num
        link_tag = a_resource.find('a', text='Link')
        if link_tag.has_attr('href'):
            res.url = link_tag['href']
            status = check_link(res.url)
            if status is not "working":
                res.has_issues = True
                temp_issues.append('{}: {}'.format(res.title, status))
        else:
            res.has_issues = True
            temp_issues.append(NO_LINK)

        details = a_resource.find('td', {'class': 'resActions'}).find('div').find('a')
        link_to_details = details['href']
        full_details = urljoin(base_url, link_to_details)
        details_page = BeautifulSoup(urlopen(full_details).read())
        res.briefDesc = find_brief_desc(details_page)
        res.abstract = find_abstract(details_page)
        if are_same(res.briefDesc, res.abstract):
            res.has_issues = True
            temp_issues.append(BD_ABSTRACT_SAME)
        res.issue_space = temp_issues
        resources.append(res)

    next_page = current_page.find_next('li').find('a')
    full_url = urljoin(base_url, next_page['href'])
    soup = BeautifulSoup(urlopen(full_url).read())
    current_page = soup.find('div', {'class': 'pagination'}).find('li', {'class': 'active'})
    page_num = current_page.find('a').text

end_time = time.time() - start_time
print('Process took {}'.format(end_time))

for resource in resources:
    if resource.has_issues:
        print('{}: {}'.format(resource.title, resource.url))
        for each in resource.issue_space:
            print("   {}".format(each))