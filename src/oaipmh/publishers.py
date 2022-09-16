from typing import Union

import datasets
import requests
from bs4 import BeautifulSoup
from requests.models import CaseInsensitiveDict

from .helpers import _peak_at_link, _check_pdf_request
from .xml_loader import OAIXMLRecordDict

logger = datasets.utils.logging.get_logger(__name__)


def get_pdf_links(record: OAIXMLRecordDict, publisher: str = "") -> list[str]:
    """Get the potential fulltext links for an OAI PMH Record
    Args:
        record (OAIXMLRecordDict): Dict representing the record
        publisher (str, optional): Publisher of the record (Used to handle link extraction). Defaults to "".

    Returns:
        list[str]: URLs pointing to the potential fulltexts
    """
    if publisher == "ubffm":

        return [x for x in record["identifiers"] if x.lower().endswith(".pdf")]

    elif publisher == "lang-sci-press":

        return [
            # check if the pdf is in the relations
            req.url
            for rel in record["relations"]
            if (
                (
                    req := _peak_at_link(  # save the request in a temporary variable  # only do a HEAD not a GET; no need to download the pdf now
                        rel.replace("index.php/Language%20Science%20Press/", "")
                    )
                )
                and _check_pdf_request(req=req)
            )
        ] or [
            # fall back to extracting the urls from the page
            req.url
            for a in BeautifulSoup(requests.get(record["id"]).content).select(
                ".item.files > .pub_format_single > .pdf"
            )
            if (
                (
                    req := _peak_at_link(  # save the request in a temporary variable
                        href
                        if isinstance(
                            str,
                            href := a[
                                "href"
                            ],  # pyright: ignore [reportGeneralTypeIssues]
                        )
                        else href[0]  # pyright: ignore [reportGeneralTypeIssues]
                    )
                )
                and _check_pdf_request(req=req)
            )
        ]

    else:

        logger.warning("Unsupported publisher")
        return []
