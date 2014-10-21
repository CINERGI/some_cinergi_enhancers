some_cinergi_enhancers
======================

Data comes in many forms. As such, the raw data that is input to an endpoint may need later fixing. In a day and age of identifiers, many pieces of metadata cna be matched to persistent URIs. There are two separate enhancing engines in this repository.

The first, Catalog Fixer, iterates through the pages of the catalog at http://hydro10.sdsc.edu/HLIResources/Resources and finds resources with issues. Issues include bad links, unsatisfactory brief descriptions and abstracts and titles that are lowercase or only acronyms. These issues have different priorities so that when the text file is output the curator will see the resources with the most sever issues at the top. URL issues (404 or redirects) are the most severe as are Duplicate resources (resources with the same title). The next most severe issues is the lack of an abstract or an all lowercase title. Lack of a brief description or only acronym in the title.

The second engine is an enhancer meant to work on CINERGI metadata objects (XML or JSON). Specifically, this enhancer validates organizations by searching the organization names in the Library of Congress database of authority headings (http://authorities.loc.gov/cgi-bin/Pwebrecon.cgi?DB=local&PAGE=First).
