__author__ = 'Raquel'


NO_LINK = 'No link'
BROKEN_LINK = 'BROKEN LINK'
BD_ABSTRACT_SAME = 'Brief Description and Abstract are the same'
ONLY_ACRONYM = 'Only acronym in title'
LOWERCASE = 'Title is lowercase'
NO_BD = 'No Brief Description'
NO_ABS = 'No Abstract'


class Issue(object):
    def __init__(self, issue):
        self.issue = issue
    severity = 0


class Duplicate(Issue):
    def __init__(self, issue):
        Issue.__init__(self, issue)
    severity = 3


class BadUrl(Issue):
    def __init__(self, url_error):
        Issue.__init__(self, url_error)
        self.error = url_error
    severity = 3


class TitleProb(Issue):
    def __init__(self, title_issue):
        Issue.__init__(self, title_issue)
        if title_issue == ONLY_ACRONYM:
            self.severity = 2
        elif title_issue == LOWERCASE:
            self.severity = 1


class SuckyDesc(Issue):
    def __init__(self, desc_issue):
        Issue.__init__(self, desc_issue)
        if desc_issue == NO_ABS:
            self.severity = 2
        else:
            self.severity = 1