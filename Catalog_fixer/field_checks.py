__author__ = 'Raquel'

import re


def tag_in_title(res_title):
    return re.search('\((DUPLICATE( [0-9])?|DEPRECATED|DELETE|BROKEN LINK|NOT FOUND|LOW REL)\)', res_title)

def are_same(bd, abstract):
    return bd == abstract