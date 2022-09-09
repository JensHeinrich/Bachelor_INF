from lxml import objectify, etree
from collections.abc import Sequence
import typing
import os
from pathlib import Path

# https://stackoverflow.com/questions/10798680/finding-text-into-namespaced-xml-elements-with-lxml-etree
NAMESPACES = {
        'oa': 'http://www.openarchives.org/OAI/2.0/',
        'dc': "http://purl.org/dc/elements/1.1/",
        'oai_dc': "http://www.openarchives.org/OAI/2.0/oai_dc/",
        'xml': 'http://www.w3.org/XML/1998/namespace',
    }

get_records = etree.XPath(
    '/oa:OAI-PMH/oa:ListRecords/oa:record',
    namespaces = NAMESPACES
)
# https://stackoverflow.com/questions/14299978/how-to-use-lxml-to-find-an-element-by-text
# https://stackoverflow.com/questions/28237694/xpath-get-parent-node-from-child-node
get_record_metadata_nodes_for_lang = etree.XPath(
        '/oa:OAI-PMH/oa:ListRecords/oa:record/oa:metadata/oai_dc:dc/'
        # + 'dc:format[text()="application/pdf"]/../' # Restrict to records marked as pdf
        'dc:language[text()=$lang]/../..',
        namespaces = NAMESPACES
    )
get_record_nodes_for_lang = etree.XPath(
        '/oa:OAI-PMH/oa:ListRecords/oa:record/oa:metadata/oai_dc:dc/'
        # +' dc:format[text()="application/pdf"]/../' # Restrict to records marked as pdf
        + 'dc:language[text()=$lang]/../../..',
        namespaces = NAMESPACES
    )
# https://lxml.de/FAQ.html#how-can-i-map-an-xml-tree-into-a-dict-of-dicts
def recursive_dict(element):
     return element.tag, \
            dict(map(recursive_dict, element)) or element.text

get_metadata_identifiers = etree.XPath(
    ".//dc:identifier/text()",
    smart_strings=False,
    namespaces=NAMESPACES
)
get_metadata_relations = etree.XPath(
    ".//dc:relation/text()",
    smart_strings=False,
    namespaces=NAMESPACES
)

get_metadata_subject = etree.XPath(
    ".//dc:subject/text()",
    smart_strings=False,
    namespaces=NAMESPACES
)

get_metadata_description = etree.XPath(
    ".//dc:description[@xml:lang=$lang ]/text()",
    smart_strings=False,
    namespaces=NAMESPACES
)

get_metadata_title = etree.XPath(
    ".//dc:title/text()",
    smart_strings=False,
    namespaces=NAMESPACES
)

get_identifiers_from_record = etree.XPath(
    '../oa:header/oa:identifier/text()', 
    namespaces = NAMESPACES)

from dataclasses import dataclass

@dataclass(kw_only=True)
class OAIXMLRecordDict:
    """Class for the records"""
    id: str
    id_: str
    identifiers: list[str]
    subject: list[str]
    title: list[str]
    description: list[str]
    relations: list[str]

    def keys(self) -> list[str]:
        return ["id","id_","identifiers","relations", *self.text_keys()]

    def text_keys(self) -> list[str]:
        """"return the keys holding the ner relevant data"""
        return ["subject","title","description"]

    # https://stackoverflow.com/questions/62560890/how-to-make-custom-data-class-subscriptable
    def __getitem__(self, item):
        return getattr(self, item)

def _parse_record(record) -> OAIXMLRecordDict:
    id = get_identifiers_from_record(record)[0]
    id_ = id.split(":")[-1]
    identifiers = get_metadata_identifiers(record)
    subject = get_metadata_subject(record)
    title = get_metadata_title(record)
    description = get_metadata_description(record, lang="eng")
    relations = get_metadata_relations(record)
 
    return OAIXMLRecordDict(
        id=id,
        id_=id_,
        identifiers = identifiers,
        subject = subject,
        title= title,
        description=description,
        relations=relations,
    )

# https://stackoverflow.com/questions/42983569/how-to-write-a-generator-class
class OAIXMLLoader:

    def __init__(
        self, 
        oai_xml_files: Sequence[
            typing.Union[
                str,
                bytes,
                os.PathLike
            ]
        ],
        lang = "deu",
        ):
        self.index = 0
        self.file_index = 0
        self.xml_files = [oai_xml_files] if isinstance(oai_xml_files, (str, bytes, os.PathLike)) else oai_xml_files
        self.lang = lang

        self.first = True
        self.records = []

    def _open_next_file(self):

        if self.first:
            next_file_idx = self.file_index
            self.first = False
        else:
            next_file_idx = self.file_index+1

        try:
            f = self.xml_files[next_file_idx]
            self.file_index=next_file_idx

        except IndexError:
            raise IndexError("No more files")

        with open(f) as file:
            self.tree = etree.parse(file)

            # Sanity check
            if self.tree.getroot().tag != '{http://www.openarchives.org/OAI/2.0/}OAI-PMH':
                raise UserWarning(f"The file {file} is not in the OAI-PMH format.")
        
            self.index = 0
            self.records = get_record_metadata_nodes_for_lang(self.tree, lang = self.lang)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            try:
                _record = self.records[self.index]
            except IndexError:
                self._open_next_file()
                _record = self.records[self.index]
            
            _idx = self.index
            _record_dict = _parse_record(_record)
            self.index += 1
            return _idx, _record_dict

        except StopIteration:
            raise StopIteration
        except IndexError:
            try:
                self._open_next_file()
            except IndexError:
                raise StopIteration


def load_xml_file_as_tuple(xml_file: typing.Union[str, bytes, os.PathLike]) -> list[tuple[OAIXMLRecordDict,typing.Any]]:

    with open(xml_file) as file:
        tree = etree.parse(file)

    if tree.getroot().tag != '{http://www.openarchives.org/OAI/2.0/}OAI-PMH':
        raise Exception(f"The file {file} is not in the OAI-PMH format.")

    records = get_record_metadata_nodes_for_lang(tree, lang ="deu")
    _records = []

    for record in records:
        _records += [(_parse_record(record), record)]
    
    if len(records) != len(_records):
        raise Exception( "Length mismatch")

    return _records 


def load_xml_file(xml_file: typing.Union[str, bytes, os.PathLike]) -> list[OAIXMLRecordDict]:

    with open(xml_file) as file:
        tree = etree.parse(file)

    if tree.getroot().tag != '{http://www.openarchives.org/OAI/2.0/}OAI-PMH':
        raise UserWarning(f"The file {file} is not in the OAI-PMH format.")

    records = get_record_metadata_nodes_for_lang(tree, lang ="deu")
    _records = []

    for record in records:
        _records += [_parse_record(record)]
    
    if len(records) != len(_records):
        raise UserWarning( "Length mismatch")

    return _records 


def load_xml_files(xml_files: Sequence[
     typing.Union[str, bytes, os.PathLike],
]) -> Sequence[tuple[OAIXMLRecordDict,]]:
    records = []

    for xml_file in xml_files:

        records += load_xml_file(xml_file)
            
    return records
