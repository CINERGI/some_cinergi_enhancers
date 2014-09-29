__author__ = 'Raquel'

def find_org(details_page):
    return details_page.find('th', text='Organization').find_next('td').text