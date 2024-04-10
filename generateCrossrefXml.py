import xml
from xml.dom.minidom import Document
from collections import namedtuple
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import time
import calendar
import re
import os
import operator
from git import *
from generatePoaXml import *
from xml_generation import *
from parsePoaXml import *
import settings

"""

"""

class crossrefXML(object):

    def __init__(self, poa_articles, pub_date = None):
        """
        set the root node
        get the article type from the object passed in to the class
        set default values for items that are boilder plate for this XML 
        """
        self.root = Element('doi_batch')

        # set the boiler plate values
        self.contrib_types = ["author"]
        self.elife_journal_id = "eLife"
        self.elife_journal_title = "eLife"
        self.elife_journal_volume = "4"
        self.elife_email_address = 'production@elifesciences.org'
        self.elife_epub_issn = "2050-084X"
        self.elife_publisher_name = "eLife Sciences Publications, Ltd"
        self.elife_crossmark_policy = "10.7554/eLife/crossmark_policy"
        self.elife_crossmark_domain = "www.elifesciences.org"

        self.root.set('version', "4.3.5")
        self.root.set('xmlns', 'http://www.crossref.org/schema/4.3.5')
        self.root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        self.root.set('xmlns:fr', 'http://www.crossref.org/fundref.xsd')
        self.root.set('xmlns:ai', 'http://www.crossref.org/AccessIndicators.xsd')
        self.root.set('xsi:schemaLocation', 'http://www.crossref.org/schema/4.3.5 http://www.crossref.org/schemas/crossref4.3.5.xsd')
        self.root.set('xmlns:mml', 'http://www.w3.org/1998/Math/MathML')

        # Publication date
        if pub_date is None:
            self.pub_date = time.gmtime()
            
        # Generate batch id
        self.elife_doi_batch_id = "elife-" + time.strftime("%Y-%m-%d-%H%M%S", self.pub_date) + "-PoA"

        # set comment
        generated = time.strftime("%Y-%m-%d %H:%M:%S")
        last_commit = get_last_commit_to_master()
        comment = Comment('generated by eLife at ' + generated + ' from version ' + last_commit)
        self.root.append(comment)

        self.build(self.root, poa_articles)

    def build(self, root, poa_articles):
        self.set_head(self.root)
        self.set_body(self.root, poa_articles)

    def set_head(self, parent):
        self.head = SubElement(parent, 'head')
        self.doi_batch_id = SubElement(self.head, 'doi_batch_id')
        self.doi_batch_id.text = self.elife_doi_batch_id
        self.timestamp = SubElement(self.head, 'timestamp')
        self.timestamp.text = time.strftime("%Y%m%d%H%M%S", self.pub_date)
        self.set_depositor(self.head)
        self.registrant = SubElement(self.head, 'registrant')
        self.registrant.text = self.elife_journal_title

    def set_depositor(self, parent):
        self.depositor = SubElement(parent, 'depositor')
        self.name = SubElement(self.depositor, 'depositor_name')
        self.name.text = self.elife_journal_title
        self.email_address = SubElement(self.depositor, 'email_address')
        self.email_address.text = self.elife_email_address

    def set_body(self, parent, poa_articles):
        self.body = SubElement(parent, 'body')
        
        for poa_article in poa_articles:
            # Create a new journal record for each article
            # Use a list of one for now
            poa_article_list = [poa_article]
            self.set_journal(self.body, poa_article_list)
        
    def get_pub_date(self, poa_article):
        """
        For using in XML generation, use the article pub date
        or by default use the run time pub date
        """
        pub_date = None
        try:
            pub_date = poa_article.get_date("pub").date
        except:
            # Default use the run time date
            pub_date = self.pub_date
        return pub_date
        
    def set_journal(self, parent, poa_articles):
        self.journal = SubElement(parent, 'journal')
        self.set_journal_metadata(self.journal)
        
        self.journal_issue = SubElement(self.journal, 'journal_issue')
        
        #self.publication_date = self.set_date(self.journal_issue, poa_article, 'publication_date')
        
        # Get the issue date from the first article in the list when doing one article per issue
        pub_date = self.get_pub_date(poa_articles[0])
        self.set_publication_date(self.journal_issue, pub_date)

        self.journal_volume = SubElement(self.journal_issue, 'journal_volume')
        self.volume = SubElement(self.journal_volume, 'volume')
        self.volume.text = self.elife_journal_volume
        
        # Add journal article
        for poa_article in poa_articles:
            self.set_journal_article(self.journal, poa_article)

    def set_journal_metadata(self, parent):
        # journal_metadata
        journal_metadata = SubElement(parent, 'journal_metadata')
        journal_metadata.set("language", "en")
        self.full_title = SubElement(journal_metadata, 'full_title')
        self.full_title.text = self.elife_journal_title
        self.issn = SubElement(journal_metadata, 'issn')
        self.issn.set("media_type", "electronic")
        self.issn.text = self.elife_epub_issn
        
    def set_journal_article(self, parent, poa_article):
        self.journal_article = SubElement(parent, 'journal_article')
        self.journal_article.set("publication_type", "full_text")
        
        # Set the title with italic tag support
        self.set_titles(self.journal_article, poa_article)

        for contrib_type in self.contrib_types:
            self.set_contributors(self.journal_article, poa_article, contrib_type)
        
        # Journal publication date
        pub_date = self.get_pub_date(poa_article)
        self.set_publication_date(self.journal_article, pub_date)
        
        self.publisher_item = SubElement(self.journal_article, 'publisher_item')
        self.identifier = SubElement(self.publisher_item, 'identifier')
        self.identifier.set("id_type", "doi")
        self.identifier.text = poa_article.doi
        
        # Disable crossmark for now
        #self.set_crossmark(self.journal_article, poa_article)
        
        #self.archive_locations = SubElement(self.journal_article, 'archive_locations')
        #self.archive = SubElement(self.archive_locations, 'archive')
        #self.archive.set("name", "CLOCKSS")
        
        self.set_fundref(self.journal_article, poa_article)
        
        self.set_doi_data(self.journal_article, poa_article)
        
        self.set_citation_list(self.journal_article, poa_article)
        
        self.set_component_list(self.journal_article, poa_article)
        
    def set_titles(self, parent, poa_article):
        """
        Set the titles and title tags allowing sub tags within title
        """
        root_tag_name = 'titles'
        tag_name = 'title'
        root_xml_element = Element(root_tag_name)
        # Crossref allows <i> tags, not <italic> tags
        tag_converted_title = replace_tags(poa_article.title, 'italic', 'i')
        tagged_string = '<' + tag_name + '>' + tag_converted_title + '</' + tag_name + '>'
        reparsed = minidom.parseString(tagged_string)

        root_xml_element = append_minidom_xml_to_elementtree_xml(
            root_xml_element, reparsed
            )

        parent.append(root_xml_element)
        
    def set_doi_data(self, parent, poa_article):
        self.doi_data = SubElement(parent, 'doi_data')
        
        self.doi = SubElement(self.doi_data, 'doi')
        self.doi.text = poa_article.doi
        
        self.resource = SubElement(self.doi_data, 'resource')
        
        resource = 'http://elifesciences.org/lookup/doi/' + poa_article.doi
        self.resource.text = resource

    def set_crossmark(self, parent, poa_article):
        self.crossmark = SubElement(parent, 'crossmark')
        
        self.crossmark_version = SubElement(self.crossmark , 'crossmark_version')
        self.crossmark_version.text = "1"
        
        self.crossmark_policy = SubElement(self.crossmark , 'crossmark_policy')
        self.crossmark_policy.text = self.elife_crossmark_policy
        
        self.crossmark_domains = SubElement(self.crossmark , 'crossmark_domains')
        self.crossmark_domain = SubElement(self.crossmark_domains , 'crossmark_domain')
        self.crossmark_domain_domain = SubElement(self.crossmark_domain , 'domain')
        self.crossmark_domain_domain.text = self.elife_crossmark_domain
        
        self.crossmark_domain_exclusive = SubElement(self.crossmark , 'crossmark_domain_exclusive')
        self.crossmark_domain_exclusive.text = "false"
        
        self.set_custom_metadata(self.crossmark, poa_article)
        
    def set_custom_metadata(self, parent, poa_article):
        self.custom_metadata = SubElement(parent, 'custom_metadata')
        
        self.ai_program = SubElement(self.custom_metadata, 'ai:program')
        self.ai_program.set('name', 'AccessIndicators')
        
        license_href = poa_article.license.href
       
        license_ref_applies_to = ['am']
        
        if license_href:
            for applies_to in license_ref_applies_to:
                self.ai_program_ref = SubElement(self.ai_program, 'ai:license_ref')
                self.ai_program_ref.set('applies_to', applies_to)
                self.ai_program_ref.text = license_href

    def set_contributors(self, parent, poa_article, contrib_type = None):
        # If contrib_type is None, all contributors will be added regardless of their type
        self.contributors = SubElement(parent, "contributors")

        # Ready to add to XML
        # Use the natural list order of contributors when setting the first author
        sequence = "first"
        for contributor in poa_article.contributors:
            if contrib_type:
                # Filter by contrib_type if supplied
                if contributor.contrib_type != contrib_type:
                    continue
            # Skip contributors with no surname
            if contributor.surname == "" or contributor.surname is None:
                # Most likely a group author
                if contributor.collab:
                    self.organization = SubElement(self.contributors, "organization")
                    self.organization.text = contributor.collab
                    self.organization.set("contributor_role", contributor.contrib_type)
                    self.organization.set("sequence", sequence)
            
            else:
                self.person_name = SubElement(self.contributors, "person_name")
    
                self.person_name.set("contributor_role", contributor.contrib_type)
                
                if contributor.corresp == True or contributor.equal_contrib == True:
                    self.person_name.set("sequence", sequence)
                else:
                    self.person_name.set("sequence", sequence)
                    
                self.given_name = SubElement(self.person_name, "given_name")
                self.given_name.text = contributor.given_name
            
                self.surname = SubElement(self.person_name, "surname")
                self.surname.text = contributor.surname
    
                if contributor.orcid:
                    self.orcid = SubElement(self.person_name, "ORCID")
                    self.orcid.set("authenticated", "true")
                    self.orcid.text = contributor.orcid
    
            # Reset sequence value after the first sucessful loop
            sequence = "additional"

    def set_publication_date(self, parent, pub_date):
        # pub_date is a python time object
        if pub_date:
            self.publication_date = SubElement(parent, 'publication_date')
            self.publication_date.set("media_type", "online")
            month = SubElement(self.publication_date, "month")
            month.text = str(pub_date.tm_mon).zfill(2)
            day = SubElement(self.publication_date, "day")
            day.text = str(pub_date.tm_mday).zfill(2)
            year = SubElement(self.publication_date, "year")
            year.text = str(pub_date.tm_year)

    def set_fundref(self, parent, poa_article):
        """
        Set the fundref data from the article funding_awards list
        """
        if len(poa_article.funding_awards) > 0:
            self.fr_program = SubElement(parent, 'fr:program')
            self.fr_program.set("name", "fundref")
            for award in poa_article.funding_awards:
                self.fr_fundgroup = SubElement(self.fr_program, 'fr:assertion')
                self.fr_fundgroup.set("name", "fundgroup")
                
                if award.get_funder_name():
                    self.fr_funder_name = SubElement(self.fr_fundgroup, 'fr:assertion')
                    self.fr_funder_name.set("name", "funder_name")
                    self.fr_funder_name.text = award.get_funder_name()
                    
                if award.get_funder_name() and award.get_funder_identifier():
                    self.fr_funder_identifier = SubElement(self.fr_funder_name, 'fr:assertion')
                    self.fr_funder_identifier.set("name", "funder_identifier")
                    self.fr_funder_identifier.text = award.get_funder_identifier()
                
                if len(award.award_ids) > 0:
                    for award_id in award.award_ids:
                        self.fr_award_number = SubElement(self.fr_fundgroup, 'fr:assertion')
                        self.fr_award_number.set("name", "award_number")
                        self.fr_award_number.text = award_id
                        
    def set_citation_list(self, parent, poa_article):
        """
        Set the citation_list from the article object ref_list objects
        """
        if len(poa_article.ref_list) > 0:
            self.citation_list = SubElement(parent, 'citation_list')
            ref_index = 0
            for ref in poa_article.ref_list:
                # Increment
                ref_index = ref_index + 1
                self.citation = SubElement(self.citation_list, 'citation')
                self.citation.set("key", str(ref_index))
                
                if ref.get_journal_title():
                    self.journal_title = SubElement(self.citation, 'journal_title')
                    self.journal_title.text = ref.get_journal_title()
                
                # Only set the first author surname
                if len(ref.authors) > 0:
                    author_surname = ref.authors[0]["surname"]
                    self.author = SubElement(self.citation, 'author')
                    self.author.text = author_surname
                    
                if ref.volume:
                    self.volume = SubElement(self.citation, 'volume')
                    self.volume.text = ref.volume
                    
                if ref.fpage:
                    self.first_page = SubElement(self.citation, 'first_page')
                    self.first_page.text = ref.fpage
                    
                if ref.year:
                    self.cyear = SubElement(self.citation, 'cYear')
                    self.cyear.text = ref.year
                    
                if ref.doi:
                    self.doi = SubElement(self.citation, 'doi')
                    self.doi.text = ref.doi

    def set_component_list(self, parent, poa_article):
        """
        Set the component_list from the article object component_list objects
        """
        if len(poa_article.component_list) <= 0:
            return

        self.component_list = SubElement(parent, 'component_list')
        for comp in poa_article.component_list:
            self.component = SubElement(self.component_list, 'component')
            self.component.set("parent_relation", "isPartOf")
            
            self.titles = SubElement(self.component, 'titles')
            
            self.title = SubElement(self.titles, 'title')
            self.title.text = comp.title
            
            if comp.subtitle:
                self.set_subtitle(self.titles, comp)
            
            if comp.mime_type:
                self.format = SubElement(self.component, 'format')
                self.format.set("mime_type", comp.mime_type)
                
            if comp.doi:
                self.doi_data = SubElement(self.component, 'doi_data')
                self.doi_tag = SubElement(self.doi_data, 'doi')
                self.doi_tag.text = comp.doi
                if comp.doi_resource:
                    self.resource = SubElement(self.doi_data, 'resource')
                    self.resource.text = comp.doi_resource
  
    def set_subtitle(self, parent, component):
        tag_name = 'subtitle'
        # Use <i> tags, not <italic> tags, <b> tags not <bold>
        if component.subtitle:
            tag_converted_string = replace_tags(component.subtitle, 'italic', 'i')
            tag_converted_string = replace_tags(tag_converted_string, 'bold', 'b')
            tag_converted_string = escape_unmatched_angle_brackets(tag_converted_string)
            tagged_string = '<' + tag_name + '>' + tag_converted_string + '</' + tag_name + '>'
            reparsed = minidom.parseString(tagged_string)

            root_xml_element = append_minidom_xml_to_elementtree_xml(
                parent, reparsed
            )
        else:
            # Empty
            self.subtitle = SubElement(parent, tag_name)

    def printXML(self):
        print self.root

    def prettyXML(self):
        encoding = 'utf-8'

        rough_string = ElementTree.tostring(self.root, encoding)
        reparsed = minidom.parseString(rough_string)

        #return reparsed.toprettyxml(indent="\t", encoding = encoding)
        return reparsed.toxml(encoding = encoding)

def build_crossref_xml_for_articles(poa_articles):
    """
    Given a list of article article objects,
    and then generate crossref XML from them
    """

    # test the XML generator 
    eXML = crossrefXML(poa_articles)
    prettyXML = eXML.prettyXML()
    
    # Write to file
    f = open(settings.TMP_DIR + os.sep + eXML.elife_doi_batch_id + '.xml', "wb")
    f.write(prettyXML)
    f.close()
    
    #print prettyXML

if __name__ == '__main__':
    
    article_xmls = ["generated_xml_output/elife_poa_e04871.xml",
                    "generated_xml_output/elife_poa_e04872.xml",
                    "generated_xml_output/elife_poa_e05224.xml",
                    "generated_xml_output/elife_poa_e06179.xml",
                    "generated_xml_output/elife02619.xml",
                    "generated_xml_output/elife02676.xml",
                    "generated_xml_output/elife01856.xml",
                    "generated_xml_output/elife00178.xml"
                    ]
    
    poa_articles = build_articles_from_article_xmls(article_xmls)
    
    # Extra sample data for testing
    for article in poa_articles:
        if article.doi == '10.7554/eLife.04871':
            # Pretend it is v2 POA, which will have a pub date
            date = datetime.datetime(2015, 2, 3)
            pub_date = date.timetuple()
            pub_type = "pub"
            date_instance = eLifeDate(pub_type, pub_date)
            article.add_date(date_instance)
    
    build_crossref_xml_for_articles(poa_articles)





