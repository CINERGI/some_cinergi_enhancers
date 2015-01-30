some_cinergi_enhancers
======================

Data comes in many forms. As such, the raw data that is input to an endpoint may need later fixing. In a day and age of identifiers, many pieces of metadata can be matched to persistent URIs.

This is a low level api of an enhancer meant to work on CINERGI metadata objects (ISO19139 XML). This enhancer validates organizations by searching the organization names in the Virtual International Authority (VIAF) database of corporate names (http://viaf.org/).

First the document is parsed for organization names which are extracted.

A post request is made with each organization name. VIAF returns an XML response which is parsed to see if the organization was found in the database and if so what is the uri. (Example uri: http://viaf.org/viaf/137536736/)

Each validated organization is then a validation that can be made to the document. For each validated organization a keyword element is created and inserted to the document. These validated organizations reference VIAF as a thesaurus. At this point the document is enhanced with new keywords.

The enhanced document is returned and saved on the local machine as 'enhanced.xml'
