__author__ = 'Raquel'

from bs4 import BeautifulSoup
from urllib.request import urlopen


def find_brief_desc(details_page):
    brief_desc = details_page.find('th', text='Brief Description').find_next('td')
    if brief_desc.text is None:
        return "No Brief Description"
    else:
        return brief_desc.text


def find_abstract(details_page):
    abstract = details_page.find('th', text='Abstract Or Purpose').find_next('td')
    if abstract.text == ".":
        return "No abstract"
    else:
        return abstract.text


def are_same(bd, abstract):
    return bd == abstract