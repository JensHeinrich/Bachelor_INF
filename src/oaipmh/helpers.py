import typing
from typing import Any, Text, Union

import datasets
import requests

from .gazetteer import Gazetteer

logger = datasets.utils.logging.get_logger(__name__)


def _peak_at_link(
    link: Union[Text, bytes],
) -> Union[requests.Response, None]:  # TODO replace with _peak_at_links
    """Peak at the provided link in an exception safe way

    Args:
        link (str): url to peak at

    Returns:
        Union[requests.Response,None]: Response of the request or None if it failed
    """
    req = None
    try:
        req = requests.head(link, allow_redirects=True)
    except Exception as N:
        logger.warning(f"Exception occured handling {link}: {N}")

    return req


def _check_pdf_request(req: requests.Response) -> bool:
    return (
        req.url.endswith(".pdf")  # dirty check for pdf
        or req.headers["Content-Type"] == "application/pdf"
    )


def _flatten(input: Union[None, list[Union[Any, list[Any]]]]) -> Union[None, list[Any]]:
    """Flatten a nested list by one level

    Args:
        input (Union[None, list[Union[Any, list[Any]]]]): List, nested List or None object to flatten

    Returns:
        Union[None, list[Any]]: List flattend by one level if nested else originial list or None
    """
    if input is None:
        return None
    if any(isinstance(elem, list) for elem in input):
        return [subelem for elem in input for subelem in elem]
    return input


def _get_largest_pdf_url(urlList: list[Union[Text, bytes]]) -> str:
    pdfUrlList = [
        (
            req.headers["Content-Length"] if "Content-Length" in req.headers else 0,
            req.url,
        )
        for target in urlList
        if (
            # dirty check if target is a pdf file
            (req := _peak_at_link(target))
            and _check_pdf_request(req=req)
        )
    ]
    if pdfUrlList == []:
        raise ValueError(f"No PDF Url in {urlList}")

    return max(
        pdfUrlList,
        key=lambda t: t[0],
    )[1]


def get_token_label_classes_from_gazetteers(
    gazetteers: dict[str, Gazetteer]
) -> list[str]:
    """Extract token labels

    Args:
        gazetteers (dict[str, Gazetteer]): dictionary of Gazetteers

    Returns:
        list[str]: Labels to use for the tokens
    """
    return [
        "O",
        *[f"I-{token_type.upper()}" for token_type in gazetteers.keys()],
        *[f"B-{token_type.upper()}" for token_type in gazetteers.keys()],
    ]


def get_link_label_classes_from_gazetteers(
    gazetteers: dict[str, Gazetteer]
) -> list[str]:
    """Extract link labels

    Args:
        gazetteers (dict[str, Gazetteer]): dictionary of Gazetteers

    Returns:
        list[str]: Labels to use for the links
    """
    # Use set to remove duplicates
    link_set = {
        link
        for token_type in gazetteers.keys()
        if (gazetteer := gazetteers[token_type])
        for entry in gazetteer
        if (link := gazetteer[entry])
    }
    return [""] + list(link_set)
