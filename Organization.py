__author__ = 'Raquel'

class Organization:
    def __init__(self, string):
        self.string = string
    uri = 0

def already_in(string, orgs):
    for o in orgs:
        if o.string == string:
            return True
    return False