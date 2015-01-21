__author__ = 'Raquel'

import xml.etree.ElementTree as ET
from urllib.request import urlopen

# character string
char_string = '{http://www.isotc211.org/2005/gco}CharacterString'


def attach_keywords(id_info, new_keywords):
    idInfo_children = list(id_info)
    idInfo_children.reverse()
    reattach = []
    while idInfo_children:
        elem = idInfo_children.pop(0)
        if elem.tag == '{http://www.isotc211.org/2005/gmd}descriptiveKeywords':
            break
        id_info.remove(elem)
        reattach.append(elem)
    id_info.append(new_keywords)
    for element in reattach:
        id_info.append(element)
    return id_info


def make_keywords(root, organizations):
    idInfo = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo').find('{http://www.isotc211.org/2005/gmd}'
                                                                                    'MD_DataIdentification')
    descriptiveKeywords = ET.SubElement(idInfo, '{http://www.isotc211.org/2005/gmd}descriptiveKeywords')
    md_keywords = ET.SubElement(descriptiveKeywords, '{http://www.isotc211.org/2005/gmd}MD_Keywords')
    for org in organizations:
        keyword = ET.SubElement(md_keywords, '{http://www.isotc211.org/2005/gmd}keyword')
        keyword_cs = ET.SubElement(keyword, char_string)
        keyword_cs.text = '{}: {}'.format(org.name, org.uri)
    keywordType = ET.SubElement(md_keywords, '{http://www.isotc211.org/2005/gmd}type')
    md_keywordType = ET.SubElement(keywordType, '{http://www.isotc211.org/2005/gmd}MD_KeywordTypeCode',
                                   {'codeList': 'http://www.isotc211.org/2005/resources/Codelist/'
                                                'gmxCodelists.xml#MD_KeywordTypeCode', 'codeListValue': 'theme'})
    md_keywordType.text = 'theme'
    thesaurus = ET.SubElement(md_keywords, '{http://www.isotc211.org/2005/gmd}thesaurusName')
    ci_citation = ET.SubElement(thesaurus, '{http://www.isotc211.org/2005/gmd}CI_Citation')
    thesaurus_title = ET.SubElement(ci_citation, '{http://www.isotc211.org/2005/gmd}title')
    thesaurusTitle_cs = ET.SubElement(thesaurus_title, char_string)
    thesaurusTitle_cs.text = 'Virtual International Authority File (VIAF) Corporate Names'
    ET.SubElement(ci_citation, '{http://www.isotc211.org/2005/gmd}date',
                  {'{http://www.isotc211.org/2005/gco}nilReason': 'unknown'})
    return attach_keywords(idInfo, descriptiveKeywords)


def enhance_xml(root, orgs):
    return make_keywords(root, orgs)
"""
def enhance_xml(root, orgs):
    oldIDInfo = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo')
    newIDInfo = make_keywords(root, orgs)
    index = list(root).index(oldIDInfo)
    root.remove(oldIDInfo)
    root.insert(index, newIDInfo)
    return root
"""