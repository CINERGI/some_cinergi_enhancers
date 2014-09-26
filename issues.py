__author__ = 'Raquel'


class Issue(object):
    def __init__(self, issue):
        self.issue = issue


class BadUrl(Issue):
    def __init__(self, url_error):
        Issue.__init__(self, url_error)
        self.error = url_error