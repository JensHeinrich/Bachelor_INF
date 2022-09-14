def label_sentence(start_idx, end_idx, sentence_label, label):
    for i in range(start_idx, end_idx):
        sentence_label[i] = label


from collections.abc import Callable, Sequence
import typing

from logging import Logger

import datasets

# FIXME import not working
from .gazetteer import Gazetteer

# Gazetteer = dict[str,str]

T = typing.TypeVar("T")  # Declare type variable

logger = datasets.utils.logging.get_logger("Matcher")


def matching_and_linking_BIO(
    gazetteer: Gazetteer,  # dictionary returning the entity identifier
    tokens: typing.Union[list[str], str],
    token_type: str,
    context_size: typing.Union[int, None] = None,
    tokenizer: Callable[[str], list[str]] = lambda x: x.split(),
    detokenizer: Callable[[list[str]], str] = lambda x: " ".join(x),
    label: typing.Union[list[str], None] = None,
    links: typing.Union[list[str], None] = None,
) -> tuple[list[str], list[str], list[str]]:
    """Dict matching based on arXiv:1906.01378

    Args:
        gazetteer (Gazetteer): Entries to match
        token_type (str): base label to use for the tokens
        context_size (typing.Union[int, None], optional): number of tokens to match. Defaults to None.
        tokenizer (function(str -> list[str]) , optional): functionn to create tokens from a String. Defaults to lambdax:x.split().
        detokenizer (function(list[str] -> str), optional): function to create strings from tokens. Defaults to lambdax:" ".join(x).
        label (typing.Union[list[str], None], optional): list of current labels. Defaults to None.
        links (typing.Union[list[str], None], optional): list of current links. Defaults to None.

    Returns:
        tuple[list[str], list[str], list[str]]: _description_
    """
    # TODO Add support for multiple gazetteers by overloading and removing the token_type

    if isinstance(tokens, str):
        _tokens = tokenizer(tokens)
    else:
        _tokens = tokens

    # normalize gazetteer for use with tokenizer and detokenizer
    _gazetteer = {detokenizer(tokenizer(key)): gazetteer[key] for key in gazetteer}

    PLACEHOLDER_LABEL = "O"
    lengths = list(set([len(tokenizer(l)) for l in _gazetteer]))
    lengths.append(0)
    lengths.sort(reverse=True)

    if context_size == None:
        context_size = max(lengths)

    # TODO use trie or other data structore to optimise matching

    i = 0
    n = len(_tokens)

    if not label:
        label = [
            PLACEHOLDER_LABEL.upper(),
        ] * n
    else:
        assert len(label) == n, "Wrong length of label list"

    if not links:
        links = [
            "",
        ] * n
    else:
        assert len(links) == n, "Wrong length of links list"

    while i < n:
        for j in lengths:
            if j <= n:
                # TODO Remove dependency on string like behaviour
                if (
                    s := detokenizer(_tokens[i : (upper_bound := min(i + j, n))])
                ) in _gazetteer:
                    logger.info(f"""Found: {s}""")
                    if label[i:upper_bound] == [PLACEHOLDER_LABEL.upper(),] * (
                        upper_bound - i
                    ):  # This way a shorter match can still be found
                        label[i:upper_bound] = [f"B-{token_type}".upper()] + [
                            f"I-{token_type}".upper()
                        ] * (upper_bound - i - 1)
                        links[i] = _gazetteer[s]
                        i = i + j + 1
                        break
                    else:
                        logger.info(
                            f"""Did not overwrite labels {label} and links {links} for {(s,gazetteer[s],token_type)} in {_tokens}"""
                        )
                        continue
                if j == 0:
                    i += 1
                    break

    return _tokens, label, links


def dict_matching(
    dictionary,
    tokens,
    context_size=None,
    PLACEHOLDER_LABEL="unlabeled",
    MATCH_LABEL="positive",
) -> tuple[Sequence[str], Sequence[str]]:
    """
    Dict matching as described in 1906.01378
    """

    if not isinstance(tokens, str):
        raise Exception("Currently only string token lists are supported")

    lengths = list(set([len(l) for l in dictionary]))
    lengths.append(0)
    lengths.sort(reverse=True)

    if context_size == None:
        context_size = max(lengths)

    # TODO use trie or other data structore to optimise matching

    i = 0
    n = len(tokens)

    label = [PLACEHOLDER_LABEL for i in range(n)]

    while i < n:

        for j in lengths:
            if j <= n - 1:
                if s := tokens[i : min(i + j, n)] in dictionary:
                    label_sentence(i, min(i + j, n), label, MATCH_LABEL)
                    i = i + j + 1
                    break
                if j == 0:
                    i += 1
                    break

    return tokens, label


class DictIdentifier:
    def __init__(self, gazetteers):
        # TODO check if tokenization is still needed
        self.gazetteers = gazetteers


class DictMatcher:
    def __init__(self, dictionary):
        # TODO check if tokenization is still needed
        self.dictionary = dictionary

    def __eq__(self, o):
        return self.dictionary == o.dictionary

    def categorize(self, sentence):
        # TODO check if tokenization is still needed
        return dict_matching(self.dictionary, sentence)
