__author__ = 'Raquel'

import xml.etree.ElementTree as ET

# character string
char_string = '{http://www.isotc211.org/2005/gco}CharacterString'


def insert_at(id_element):
    # Return the index of the last keywords in MD_DataIdentificationInfo
    idInfo_children = list(id_element)
    idInfo_children.reverse()
    while idInfo_children:
        elem = idInfo_children.pop(0)
        if elem.tag == '{http://www.isotc211.org/2005/gmd}descriptiveKeywords':
            return (list(id_element).index(elem)) + 1


def insert_new_keywords(root, new_keywords):
    MD_IDinfo = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo').find('{http://www.isotc211.org/'
                                                                                       '2005/gmd}MD_DataIdentification')
    # Find the index of last keywords and insert new keywords after these
    index = insert_at(MD_IDinfo)
    MD_IDinfo.insert(index, new_keywords)
    return MD_IDinfo


def make_keywords(organizations):
    descriptiveKeywords = ET.Element('{http://www.isotc211.org/2005/gmd}descriptiveKeywords')
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
    return descriptiveKeywords


def enhance_xml(root, orgs):
    new_keywords = make_keywords(orgs)
    insert_new_keywords(root, new_keywords)