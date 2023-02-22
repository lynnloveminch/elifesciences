Feature: Generate POA XML
  In order to generate XML
  As a user
  I want to use the XML generation libraries

  Scenario: Check settings exist and their value
    Given I have settings
    When I read settings <property>
    Then I have the value <value>
    
  Examples:
    | property                                    | value
    | ROWS_WITH_COLNAMES                          | 3
    | LESS_THAN_ESCAPE_SEQUENCE                   | LTLT
    | GREATER_THAN_ESCAPE_SEQUENCE                | GTGT

  Scenario: Override settings values
    Given I have settings
    When I set settings <property> to <value>
    And I read settings <property>
    Then I have the value <value>
    
  Examples:
    | property                                    | value
    | LESS_THAN_ESCAPE_SEQUENCE                   | foo
    | XLS_PATH                                    | test_data/

  Scenario: Override json settings values
    Given I have settings
    When I set json settings <property> to <value>
    And I read settings <property>
    Then I have the json value <value>
    
  Examples:
    | property                                    | value
    | XLS_FILES                                   | {"authors" : "poa_author.csv", "license" : "poa_license.csv", "manuscript" : "poa_manuscript.csv", "received" : "poa_received.csv", "subjects" : "poa_subject_area.csv", "organisms": "poa_research_organism.csv"}

  Scenario: Test entity to unicode conversion
    Given I have the string <string>
    When I convert the string with entities to unicode
    Then I have the unicode <unicode>

  Examples:
    | string                                      | unicode
    | muffins                                     | muffins
    | Coffe Ho&#x00FC;se                          | Coffe Hoüse
    | Edit&#x00F3;rial&#x00F3; Department&#x00F3; | Editórialó Departmentó
    
  Scenario: Angle bracket escape sequence conversion
    Given I have the string <string>
    And I reload settings
    When I decode the string with decode brackets
    Then I have the decoded string <decoded_string>
    
  Examples:
    | string                                      | decoded_string
    | LTLT                                        | <
    | GTGT                                        | >
    | LTLTGTGT                                    | <>
    | LTLTiGTGTeyeLTLT/iGTGT                      | <i>eye</i>
    | LTLTiGTGTNicotiana attenuataLTLT/iGTGT      | <i>Nicotiana attenuata</i>
    | YLTLTsupGTGT1LTLT/supGTGTSLTLTsupGTGT2LTLT/supGTGTPLTLTsupGTGT3LTLT/supGTGTTLTLTsupGTGT4LTLT/supGTGTSLTLTsupGTGT5LTLT/supGTGTPLTLTsupGTGT6LTLT/supGTGTSLTLTsupGTGT7LTLT/supGTGT repeats                         | Y<sup>1</sup>S<sup>2</sup>P<sup>3</sup>T<sup>4</sup>S<sup>5</sup>P<sup>6</sup>S<sup>7</sup> repeats
    
  Scenario: Parse CSV files
    Given I have settings
    And I reload settings
    And I set settings XLS_PATH to test_data/
    And I set json settings XLS_FILES to {"authors" : "poa_author.csv", "license" : "poa_license.csv", "manuscript" : "poa_manuscript.csv", "received" : "poa_received.csv", "subjects" : "poa_subject_area.csv", "organisms": "poa_research_organism.csv", "abstract": "poa_abstract.csv", "title": "poa_title.csv"}
    And I reload XML generation libraries
    And I have article_id <article_id>
    And I have author_id <author_id>
    When I set attribute to parseCSVFiles method <method_name>
    Then I have attribute <attribute>
    
  Examples:
    | article_id    | author_id  | method_name             | attribute
    | 00003         |            | get_title               | This, 'title, includes "quotation", marks
    | 00007         |            | get_title               | Herbivory-induced "volatiles" function as defenses increasing fitness of the native plant LTLTiGTGTNicotiana attenuataLTLT/iGTGT in nature
    | 00003         | 1258       | get_author_first_name   | Preetha
    | 00012         |            | get_license             | 1
    | 00007         |            | get_organisms           | Other
    | 00003         |            | get_organisms           | B. subtilis,D. melanogaster,E. coli,Mouse
    | 00007         |            | get_subjects            | Genomics and evolutionary biology,Plant biology
    | 00007         |            | get_abstract            | An abstract with some "quotation" marks
    | 00012         |            | get_abstract            | In this abstract are consensus YLTLTsupGTGT1LTLT/supGTGTSLTLTsupGTGT2LTLT/supGTGTPLTLTsupGTGT3LTLT/supGTGTTLTLTsupGTGT4LTLT/supGTGTSLTLTsupGTGT5LTLT/supGTGTPLTLTsupGTGT6LTLT/supGTGTSLTLTsupGTGT7LTLT/supGTGT repeats, LTLTiGTGTDrosophilaLTLT/iGTGT and "quotations".