__author__ = 'Raquel'

from bs4 import BeautifulSoup
from urllib.request import urlopen


def find_brief_desc(details_page):
    return details_page.find('th', text='Brief Description').find_next('td').text


def find_abstract(details_page):
    return details_page.find('th', text='Abstract Or Purpose').find_next('td').text


def are_same(bd, abstract):
    return bd == abstract