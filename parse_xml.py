__author__ = 'Raquel'

from Organization import Organization, already_in
import re

# VIAF base url
viaf_base = 'http://viaf.org/viaf/search'

# string for searching corporate names
corporate_names = 'local.corporateNames'

# String for searching all of viaf
all_viaf = 'all'

# character string
char_string = '{http://www.isotc211.org/2005/gco}CharacterString'

# NCDC resource
# http://hydro10.sdsc.edu/metadata/National_Climatic_Data_Center/23759C9A-F801-495B-B140-9A41637E3D7C.xml
# CZO resource
# http://hydro10.sdsc.edu/metadata/Critical_Zone_Observatory_Catalog/159C0A40-C9AC-4161-914B-193FBAC9C1D1.xml


def parse_xml(root, orgs):
    # find two elements with Responsible Party: contact and identification info
    contact = root.find('{http://www.isotc211.org/2005/gmd}contact')
    idInfo = root.find('{http://www.isotc211.org/2005/gmd}identificationInfo').find('{http://www.isotc211.org/2005/gmd}'
                                                                                    'MD_DataIdentification')
    if contact is None or idInfo is None:
        return False

    # Dictionary with parent elements as keys
    orgs_found = {}

    # in contact, CI_ResponsibleParty is direct child
    # Access this child then access the organisationName, characterString and text
    contact_rp = contact.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty')
    contact_orgs = contact_rp.find('{http://www.isotc211.org/2005/gmd}organisationName').\
        find('{http://www.isotc211.org/2005/gco}CharacterString').text
    orgs_found[contact_rp] = contact_orgs

    # in idInfo, CI_ResponsibleParty is part of citation and pointOfContact
    citation = idInfo.find('{http://www.isotc211.org/2005/gmd}citation').find('{http://www.isotc211.org/2005/gmd}'
                                                                              'CI_Citation')

    citation_rp = citation.find('{http://www.isotc211.org/2005/gmd}citedResponsibleParty')

    if citation_rp is not None:
        more_orgs = citation_rp.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty').\
            find('{http://www.isotc211.org/2005/gmd}organisationName').\
            find('{http://www.isotc211.org/2005/gco}CharacterString').text
        orgs_found[citation_rp] = more_orgs

    # Find all points of contact
    pointsOfContact = idInfo.findall('{http://www.isotc211.org/2005/gmd}pointOfContact')

    for each in pointsOfContact:
        poc_rp = each.find('{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty')
        orgName = poc_rp.find('{http://www.isotc211.org/2005/gmd}organisationName')
        if orgName is not None:
            orgs_found[poc_rp] = orgName.find('{http://www.isotc211.org/2005/gco}CharacterString').text

    for k in orgs_found:
        orgs_found[k] = re.split('[^a-zA-Z\s\d:.]', orgs_found[k])
        for each in orgs_found[k]:
            if re.match('(^\s|\s$)', each):
                # remove spaces from org
                no_spaces = each.rstrip().lstrip()
                if not already_in(no_spaces, orgs):
                    new_org = Organization(no_spaces)
                    if new_org.validate_in_viaf():
                        orgs.append(new_org)
            else:
                if not already_in(each, orgs):
                    new_org = Organization(each)
                    if new_org.validate_in_viaf():
                        orgs.append(new_org)
    return True