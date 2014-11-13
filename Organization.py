__author__ = 'Raquel'

import re

class Organization:
    def __init__(self, name):
        self.name = name
        self.string = '{}'.format(name)
    link = 0
    uri = link


def already_in(string, orgs):
    for o in orgs:
        if o.name == string:
            return True
    return False


def pseudo_encode(string):
    return re.sub('\s', '%2B', string)