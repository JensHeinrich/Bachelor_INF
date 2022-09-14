from lxml import etree
import typing
from typing import Union
import os


# https://stackoverflow.com/questions/10798680/finding-text-into-namespaced-xml-elements-with-lxml-etree
NAMESPACES = {
    "oa": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

# https://stackoverflow.com/questions/14299978/how-to-use-lxml-to-find-an-element-by-text
# https://stackoverflow.com/questions/28237694/xpath-get-parent-node-from-child-node
get_record_metadata_nodes_for_lang = etree.XPath(
    "/oa:OAI-PMH/oa:ListRecords/oa:record/oa:metadata/oai_dc:dc/"
    # + 'dc:format[text()="application/pdf"]/../' # Restrict to records marked as pdf
    "dc:language[text()=$lang]/../..",
    namespaces=NAMESPACES,
)

# https://lxml.de/FAQ.html#how-can-i-map-an-xml-tree-into-a-dict-of-dicts
def recursive_dict(
    element: etree._Element,
) -> tuple[str, Union[dict, str, None]]:
    """Helper function to display xml entry in an easier to read format

    Args:
        element (etree._Element): XML element

    Returns:
        tuple[str, Union[dict[str, Any], str]]: tag of the element and a proper representation
    """

    return element.tag, dict(map(recursive_dict, element)) or element.text


# Helper "functions" to get the fields of OAI PMH xml record
get_metadata_identifiers = etree.XPath(
    ".//dc:identifier/text()", smart_strings=False, namespaces=NAMESPACES
)
get_metadata_relations = etree.XPath(
    ".//dc:relation/text()", smart_strings=False, namespaces=NAMESPACES
)

get_metadata_subject = etree.XPath(
    ".//dc:subject/text()", smart_strings=False, namespaces=NAMESPACES
)

get_metadata_description = etree.XPath(
    ".//dc:description[@xml:lang=$lang ]/text()",
    smart_strings=False,
    namespaces=NAMESPACES,
)

get_metadata_title = etree.XPath(
    ".//dc:title/text()", smart_strings=False, namespaces=NAMESPACES
)

get_identifiers_from_record = etree.XPath(
    "../oa:header/oa:identifier/text()", namespaces=NAMESPACES
)

from dataclasses import dataclass


@dataclass(kw_only=True)
class OAIXMLRecordDict:
    """Class for the OAI PMH records"""

    id: str
    id_: str
    identifiers: list[str]
    subject: list[str]
    title: list[str]
    description: list[str]
    relations: list[str]

    def keys(self) -> list[str]:
        return ["id", "id_", "identifiers", "relations", *self.text_keys()]

    def text_keys(self) -> list[str]:
        """ "return the keys holding the NER relevant data"""
        return ["subject", "title", "description"]

    # https://stackoverflow.com/questions/62560890/how-to-make-custom-data-class-subscriptable
    def __getitem__(self, item):
        return getattr(self, item)


def _parse_record(record: etree._Element) -> OAIXMLRecordDict:
    """Parse an xml element to a dict

    Args:
        record (lxml.etree._Element): OAI PMH record

    Returns:
        OAIXMLRecordDict: dictionary containing the metadata of an OAI PMH record
    """
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
        identifiers=identifiers,
        subject=subject,
        title=title,
        description=description,
        relations=relations,
    )


def load_xml_file(
    xml_file: typing.Union[str, bytes, os.PathLike]
) -> list[OAIXMLRecordDict]:
    """Return the records contained in a OAI PMH XML file

    Args:
        xml_file (typing.Union[str, bytes, os.PathLike]): Path to an OAI PMH XML file

    Raises:
        UserWarning: Warning in wrong xml format
        UserWarning: Warning on a parsing error

    Returns:
        list[OAIXMLRecordDict]: List of the extracted OAI PMH records
    """

    with open(xml_file) as file:
        tree = etree.parse(file)

    if tree.getroot().tag != "{http://www.openarchives.org/OAI/2.0/}OAI-PMH":
        raise UserWarning(f"The file {file} is not in the OAI-PMH format.")

    records: list[etree._Element] = get_record_metadata_nodes_for_lang(tree, lang="deu")
    _records: list[OAIXMLRecordDict] = [_parse_record(r) for r in records]

    if len(records) != len(_records):
        raise UserWarning("Length mismatch")

    return _records
