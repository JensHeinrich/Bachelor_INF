import typing


from typing import Union, Text, Any
from .gazetteer import Gazetteer


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


import requests


def _get_largest_pdf_url(urlList: list[Union[Text, bytes]]) -> str:
    pdfUrlList = [
        (
            req.headers["Content-Length"] if "Content-Length" in req.headers else 0,
            req.url,
        )
        for target in urlList
        if (
            # dirty check if target is a pdf file
            (req := requests.head(target, allow_redirects=True)).url.endswith(".pdf")
            or req.headers["Content-Type"] == "application/pdf"
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
