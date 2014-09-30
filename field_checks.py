__author__ = 'Raquel'

import re


def tagged(res_title):
    return re.search('\((DUPLICATE( [0-9])?|DEPRECATED|BROKEN LINK|LOW REL)\)', res_title)


def are_same(bd, abstract):
    return bd == abstract