import requests
from bs4 import BeautifulSoup

import datasets

logger = datasets.utils.logging.get_logger(__name__)


def get_pdf_links(record, publisher: str = "") -> list[str]:

    if publisher == "ubffm":

        return [
            x
            for x in record["identifiers"]
            if x.lower().endswith(".pdf")
        ]

    elif publisher == "lang-sci-press":

        return (
            [
                # check if the pdf is in the relations
                req.url
                for rel in record["relations"]
                if (
                    req := requests.head(  # save the request in a temporary variable  # only do a HEAD not a GET; no need to download the pdf now
                        rel.replace("index.php/Language%20Science%20Press/", "")
                    )
                ).headers["Content-Type"]
                == "application/pdf"  # only get links pointing to pdf
            ] or [
                # fall back to extracting the urls from the page
                req.url
                for a in BeautifulSoup(
                    requests.get(record["id"]).content
                ).select(".item.files > .pub_format_single > .pdf")
                if (
                    req := requests.head(  # save the request in a temporary variable
                        href if isinstance(str, href:=a["href"]) else href[0] # pyright: ignore [reportGeneralTypeIssues]
                    )  # only do a HEAD not a GET; no need to download the pdf now
                ).headers["Content-Type"]
                == "application/pdf"  # only get links pointing to pdf
            ]
        )

    else:

        logger.warning("Unsupported publisher")
        return []