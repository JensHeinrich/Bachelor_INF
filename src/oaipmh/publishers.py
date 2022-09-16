from typing import Union

import datasets
import requests
from bs4 import BeautifulSoup
from requests.models import CaseInsensitiveDict

from .xml_loader import OAIXMLRecordDict

logger = datasets.utils.logging.get_logger(__name__)


def _peak_at_link(
    link: str,
) -> Union[requests.Response, None]:  # TODO replace with _peak_at_links
    """Peak at the provided link in an exception safe way

    Args:
        link (str): url to peak at

    Returns:
        Union[requests.Response,None]: Response of the request or None if it failed
    """
    req = None
    try:
        req = requests.head(link)
    except Exception as N:
        logger.warning(f"Exception occured handling {link}: {N}")

    return req


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
                and req.headers["Content-Type"]
                == "application/pdf"  # only get links pointing to pdf
            )
        ] or [
            # fall back to extracting the urls from the page
            req.url
            for a in BeautifulSoup(requests.get(record["id"]).content).select(
                ".item.files > .pub_format_single > .pdf"
            )
            if (
                (
                    req := _peak_at_links(  # save the request in a temporary variable
                        href
                        if isinstance(
                            str,
                            href := a[
                                "href"
                            ],  # pyright: ignore [reportGeneralTypeIssues]
                        )
                        else href[0]  # pyright: ignore [reportGeneralTypeIssues]
                    )  # only do a HEAD not a GET; no need to download the pdf now
                )
                and req.headers["Content-Type"]
                == "application/pdf"  # only get links pointing to pdf
            )
        ]

    else:

        logger.warning("Unsupported publisher")
        return []
