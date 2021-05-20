import xml
from xml.dom.minidom import Document
from collections import namedtuple
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom

"""
create classes to represent affiliations, authors and papers.
pass the compount object to a calss that writes the XML in the expected format. 

## GOTCHAS/TODOs

self.orcid.set("xlink:href", contributor.orcid) returns an error

in aff, determine why some elements take an enclosing addr-line, and others don't 

in aff, if email is associated with aff, how do we deal with two atuhors from the same place,
but with different emails?

Think about moving the function that adds the doctype out of the funciton that 
does pretty printing. 
"""

class eLife2XML(object):
    root = Element('article')

    def __init__(self, poa_article):
        """
        set the root node
        get the article type from the object passed in to the class
        set default values for items that are boilder plate for this XML 
        """

        # set the boiler plate values
        self.journal_id_types = ["nlm-ta", "hwp", "publisher-id"]
        self.elife_journal_id = "eLife"
        self.elife_journal_title = "eLife"
        self.elife_epub_issn = "2050-084X"
        self.elife_publisher_name = "eLife Sciences Publications, Ltd"

        self.root.set('article-type', poa_article.articleType)
        comment = Comment('generated by eLife')
        self.root.append(comment)
        self.build(self.root, poa_article)

    def build(self, root, poa_article):
        self.set_frontmatter(self.root, poa_article)
        # self.set_title(self.root, poa_article)

    def set_frontmatter(self, parent, poa_article):
        self.front = SubElement(parent, 'front')
        self.set_journal_meta(self.front)
        self.set_article_meta(self.front, poa_article)        

    def set_article_meta(self, parent, poa_article):
        self.article_meta = SubElement(parent, "article-meta")
        #
        self.title_group = SubElement(parent, "title-group")
        self.title = SubElement(self.title_group, "title")
        self.title.text = poa_article.title 
        #
        self.set_contrib_group(parent, poa_article)
        #
        self.set_abstract = SubElement(parent, "abstract")
        self.set_para = SubElement(self.set_abstract, "p")
        self.set_para.text = poa_article.abstract

    def set_journal_meta(self, parent):
        """
        take boiler plate values from the init of the calss 
        """
        self.journal_meta = SubElement(parent, "journal-meta")

        # journal-id
        for journal_id_type in self.journal_id_types:
            self.journal_id = SubElement(self.journal_meta, "journal_id") 
            self.journal_id.text = self.elife_journal_id 
            self.journal_id.set("journal-id-type", journal_id_type) 

        # title-group
        self.issn = SubElement(parent, "issn")
        self.issn.text = self.elife_epub_issn
        self.issn.set("pub-type", "epub")

        # publisher
        self.publisher = SubElement(parent, "publisher")
        self.publisher_name = SubElement(self.publisher, "publisher_name")
        self.publisher_name.text = self.elife_publisher_name

    def set_contrib_group(self, parent, poa_article):
        self.contrib_group = SubElement(parent, "contrib_group")

        for contributor in poa_article.contributors:
            self.contrib = SubElement(self.contrib_group, "contrib")

            self.contrib.set("contrib-type", contributor.contrib_type)
            if contributor.corresp == True:
                self.contrib.set("corresp", "yes")
            if contributor.equal_contrib == True:
                self.contrib.set("equal_contrib", "yes")
            if contributor.auth_id:
                self.contrib.set("auth_id", contributor.auth_id)

            self.name = SubElement(self.contrib, "name")
            self.surname = SubElement(self.name, "surname")
            self.surname.text = contributor.surname
            self.given_name = SubElement(self.name, "given-name")
            self.given_name.text = contributor.given_name

            if contributor.orcid:
                self.orcid = SubElement(self.contrib, "uri")
                self.orcid.set("content-type", "orcid")
                self.orcid.set("""xlink-href""", contributor.orcid) # TODO: figure out why we can't set ':' within an attribute name

            for affiliation in contributor.affiliations:
                self.aff = SubElement(self.contrib, "aff")

                if affiliation.department:
                    self.addline = SubElement(self.aff, "addr-line")
                    self.department = SubElement(self.addline, "named-content")
                    self.department.set("content-type", "department")
                    self.department.text = affiliation.department

                if affiliation.institution:
                    self.institution = SubElement(self.aff, "institution")
                    self.institution.text = affiliation.institution

                if affiliation.city:
                    self.addline = SubElement(self.aff, "addr-line")
                    self.city = SubElement(self.addline, "named-content")
                    self.city.set("content-type", "city")
                    self.city.text = affiliation.city

                if affiliation.country:
                    self.country = SubElement(self.aff, "country")
                    self.country.text = affiliation.country

                if affiliation.phone:
                    self.phone = SubElement(self.aff, "phone")
                    self.phone.text = affiliation.phone

                if affiliation.fax:
                    self.fax = SubElement(self.aff, "fax")
                    self.fax.text = affiliation.fax                    

                if affiliation.email:
                    self.email = SubElement(self.aff, "email")
                    self.email.text = affiliation.email

    def printXML(self):
        print self.root

    def prettyXML(self):
        doctype = minidom.getDOMImplementation('').createDocumentType(
            'article', '-//NLM//DTD Journal Archiving and Interchange DTD v3.0 20080202//EN',
            'http://dtd.nlm.nih.gov/archiving/3.0/archivearticle3.dtd')

        rough_string = ElementTree.tostring(self.root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        if doctype:
            reparsed.insertBefore(doctype, reparsed.documentElement)
        return reparsed.toprettyxml(indent="\t")

class ContributorAffiliation():
    phone = None
    fax = None
    email = None 

    department = None
    institution = None
    city = None 
    country = None

class eLifePOSContributor():
    """
    Currently we are not sure that we can get an auth_id for 
    all contributors, so this attribute remains an optional attribute. 
    """

    corresp = False
    equal_contrib = False

    auth_id = None
    orcid = None

    def __init__(self, contrib_type, surname, given_name):
        self.contrib_type = contrib_type
        self.surname = surname
        self.given_name = given_name
        self.affiliations = []

    def set_affiliation(self, affiliation):
        self.affiliations.append(affiliation)

class eLifePOA():
    """
    We include some boiler plate in the init, namely articleType
    """
    contributors = [] 

    def __init__(self, doi, title):
        self.articleType = "research-article"
        self.doi = doi 
        self.contributors = [] 
        self.title = title 
        self.abstract = ""

    def add_contributor(self, contributor):
        self.contributors.append(contributor)

if __name__ == '__main__':

    # test affiliations 
    aff1 = ContributorAffiliation()
    aff1.department = "Editorial Department"
    aff1.institution = "eLife"
    aff1.city = "Cambridge"
    aff1.country = "UK"
    aff1.email = "m.harrsion@elifesciecnes.org"

    aff2 = ContributorAffiliation()
    aff2.department = "Coffe House"
    aff2.institution = "hipster"
    aff2.city = "London"
    aff2.country = "UK"
    aff2.email = "m.harrsion@elifesciecnes.org"

    aff3 = ContributorAffiliation()
    aff3.department = "Coffe House"
    aff3.institution = "hipster"
    aff3.city = "London"
    aff3.country = "UK"
    aff3.email = "i.mulvany@elifesciences.org"


    # test authors 
    auth1 = eLifePOSContributor("author", "Harrison", "Melissa")
    auth1.auth_id = "029323as"
    auth1.corresp = True
    auth1.orcid = "this is an orcid"
    auth1.set_affiliation(aff1)
    auth1.set_affiliation(aff2)

    auth2 = eLifePOSContributor("author", "Mulvany", "Ian")
    auth2.auth_id = "ANOTHER_ID_2"
    auth2.corresp = True
    auth2.set_affiliation(aff3)


    # test article 
    doi = "http://dx.doi.org/http://dx.doi.org/10.7554/eLife.00929"
    title = "The Test Title"
    newArticle = eLifePOA(doi, title)

    newArticle.add_contributor(auth1)
    newArticle.add_contributor(auth2)

    # test the XML generator 
    eXML = eLife2XML(newArticle)
    prettyXML = eXML.prettyXML()
    print prettyXML




