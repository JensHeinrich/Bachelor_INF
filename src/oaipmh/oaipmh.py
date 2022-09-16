import json
import os
import re
import typing
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any, List, Union

import datasets
import requests
from datasets.tasks.base import T

from .extract_pdf import get_text_from_pdf
from .gazetteer import Gazetteer, read_gazetteers
from .helpers import (
    _flatten,
    _get_largest_pdf_url,
    get_link_label_classes_from_gazetteers,
    get_token_label_classes_from_gazetteers,
)
from .publishers import get_pdf_links
from .xml_loader import OAIXMLRecordDict, load_xml_file

if __name__ == "__main__" and __package__ is None:
    __package__ = "expected.package.name"


logger = datasets.utils.logging.get_logger(__name__)

_CITATION = """\
    @unpublished{
        author = {Jens Heinrich},
        title = {Analyse der Möglichkeit einer automatischen Anreicherung von sprachwissenschaftlichen Texten durch Named Entity Recognition unter Verwendung von BERT mit Semantik aus der BLL Ontologie},
        type = {Bachelorthesis},
    }
"""

_DESCRIPTION = """\
Dataset using OAI PMH entries
"""

from pathlib import Path

from .dict_matcher import matching_and_linking_BIO


class OAIPMHConfig(
    datasets.BuilderConfig  # pyright: ignore [reportPrivateImportUsage] # TODO wait for fix for https://github.com/huggingface/datasets/issues/3841
):
    def __init__(
        self,
        # citation,
        # url,
        publisher: str = "",
        extract_fulltexts: bool = False,
        do_string_match: bool = False,
        language: typing.Union[str, None] = "all",
        size: typing.Union[int, None] = None,
        token_label_classes: Union[List[str], None] = None,
        link_label_classes: Union[List[str], None] = None,
        gazetteers: Union[dict[str, Gazetteer], None] = None,
        oaipmh_xml_files: Union[list[Path], list[str], None] = None,
        gazetteer_files: Union[list[Path], list[str], None] = None,
        time_log: Union[Path, str, None] = None,
        **config_kwargs,
    ):
        """BuilderConfig for OAI PMH datasets class

        Args:
            publisher (str): publisher of the records (used to find the pdf)
            extract_fulltexts (bool): toggle to enable text extraction from the pdf files
            do_string_match (bool): toggle to enable creation of labels by using string matching
            language (typing.Union[str, None], optional): _description_. Defaults to "all".
            size (typing.Union[int, None], optional): number of entries to use. Defaults to None.
            token_label_classes (Union[List[str], None], optional): list of labels used by the dataset for NER tags. Defaults to None.
            link_label_classes (Union[List[str], None], optional): list of labels used by the dataset for NER links. Defaults to None.
            gazetteers (Union[dict[str, Gazetteer], None], optional): gazetteers used for string matching. Defaults to None.
            oaipmh_xml_files (Union[list[Path],list[str],None]), optional): OAI PMH XML Files containing the records. Defaults to None.
            gazetteer_files (Union[list[Path],list[str],None]), optional): Files containing the gazetteers. Defaults to None.
            time_log (Union[Path,str,None]): Path to log timings to. Defaults to None.

            **kwargs: Arguments passed to the parent class


        Raises:
            UserWarning: StringMatching not possible without gazetteer
            UserWarning: labels could not be found

        """

        super(OAIPMHConfig, self).__init__(**config_kwargs)

        self.publisher = publisher
        self.language = language
        self.extract_fulltexts = extract_fulltexts

        self.do_string_match = do_string_match

        self.size = size

        if gazetteers is None:
            if gazetteer_files is not None:
                gazetteers = read_gazetteers(gazetteer_files)

        if gazetteers is None:
            if do_string_match:
                raise UserWarning(f"String matching cannot be done without a gazetteer")

            if token_label_classes is None or link_label_classes is None:
                raise UserWarning(
                    """No `token_label_classes` and / or `link_label_classes` are defined.
                    Pass them as argument or provide either `gazetteers` or `gazetteer_files` to have them extracted.
                    """
                )

        else:  # gazetteers is not None

            if token_label_classes is None:
                token_label_classes = get_token_label_classes_from_gazetteers(
                    gazetteers
                )

            if link_label_classes is None:
                link_label_classes = get_link_label_classes_from_gazetteers(gazetteers)

        self.gazetteers = gazetteers
        self.token_label_classes = token_label_classes
        self.link_label_classes = link_label_classes

        self.oaipmh_xml_files = oaipmh_xml_files

        self.version = "0.4.0"

        self.publisher = publisher

        if time_log is not None:
            # ensure the file be created
            time_log = Path(time_log).expanduser().absolute()
            time_log.parent.mkdir(parents=True, exist_ok=True)
            # create file and header
            with open(time_log, "w") as f:
                f.write(
                    """
                # Timings are logged as JSON objects
                # One object per line
                """
                )
        self.time_log = time_log

        # TODO Check if pickle helper still needed
        def __getstate__(self):
            state = self.__dict__.copy()

            del state["tokenizer"]
            del state["_get_pdf_links"]
            del state["matcher"]

            return state

        def __setstate__(self, state):
            self.__dict__.update(state)


class OAIPMH(
    datasets.GeneratorBasedBuilder  #  pyright: ignore [reportPrivateImportUsage] # TODO wait for fix for https://github.com/huggingface/datasets/issues/3841
):

    VERSION = datasets.Version("2.4.0")

    BUILDER_CONFIG_CLASS = OAIPMHConfig

    def _info(self):

        features = dict()

        features.update(
            {
                "id_": datasets.Value("string"),
                "id": datasets.Value("string"),
                "identifiers": datasets.Sequence(feature=datasets.Value("string")),
                "relations": datasets.Sequence(feature=datasets.Value("string")),
            }
        )

        for field in [
            "all",
            "title",
            "subject",
            "description",
            *(["text"] if self.config.extract_fulltexts else []),
        ]:
            if self.config.do_string_match:
                features.update(
                    {
                        f"{field}_tokens": datasets.Sequence(datasets.Value("string")),
                        f"{field}_ner_tags": datasets.Sequence(
                            datasets.features.ClassLabel(
                                names=self.config.token_label_classes
                            )
                        ),
                        f"{field}_ner_links": datasets.Sequence(
                            datasets.features.ClassLabel(
                                names=self.config.link_label_classes
                            )
                        ),
                    }
                )

            else:

                features.update(
                    {f"{field}": datasets.Sequence(datasets.Value("string"))}
                )

        return datasets.DatasetInfo(  # pyright: ignore [reportPrivateImportUsage] # TODO wait for fix for https://github.com/huggingface/datasets/issues/3841
            description=_DESCRIPTION,
            features=datasets.Features(features),
            # TODO
            # No default supervised_keys (as we have to pass both question
            # and context as input).
            supervised_keys=None,
            # FIXME homepage="URL",
            citation=_CITATION,
            # TODO add task_templates
        )

    def _split_generators(
        self, dl_manager: datasets.DownloadManager
    ) -> Sequence[
        datasets.SplitGenerator  # pyright: ignore [reportPrivateImportUsage] # TODO wait for fix for https://github.com/huggingface/datasets/issues/3841
    ]:
        # TODO use API directly, e.g. with sickle
        # TODO use streaming generator to load files only if needed

        self.config: OAIPMHConfig  # Type hint

        if self.config.oaipmh_xml_files is None:
            # inspired by https://huggingface.co/datasets/matinf/blob/main/matinf.py#L134
            if not (
                dl_manager.manual_dir is not None
                and (
                    data_dir := Path(dl_manager.manual_dir).expanduser().absolute()
                ).exists()
            ):
                raise FileNotFoundError(
                    f"""{data_dir if data_dir else 'data_dir'} does not exist. 
                    Make sure you either provide oaipmh_xml_files or insert a manual dir via `datasets.load_dataset('oaipmh', data_dir=...)` that includes an `xml` directory containing the OAI-PMH XML-Files. 
                    You can get those by using [oaipmharvest](https://github.com/ubffm/oaipmharvest).
                    A `gazetteers` directory containing the gazetteers is also required for the string matching functionality to work. Manual download instructions: {self.manual_download_instructions}"""
                )

            self.config.oaipmh_xml_files = list(data_dir.joinpath("xml").glob("*.xml"))

        start_time = datetime.now()
        mapped = list(
            datasets.utils.py_utils.map_nested(
                load_xml_file,
                self.config.oaipmh_xml_files,
                num_proc=16,
                desc="Parsing XML files",
                disable_tqdm=not datasets.utils.logging.is_progress_bar_enabled(),
            )
        )

        _records = _flatten(mapped)

        duration = datetime.now() - start_time

        if _records is None:
            raise Exception(f"Error handling the records")

        logger.warning(
            f"""Parsed {len(list(self.config.oaipmh_xml_files))} files to  {len(mapped)} lists containing {len(_records)} records in {duration.total_seconds()} s."""
        )
        if self.config.time_log is not None:
            with open(self.config.time_log, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "from_type": "xml",
                            "from": "files",
                            "to": "lists",
                            "from_count": len(list(self.config.oaipmh_xml_files)),
                            "to_count": len(mapped),
                            "duration": duration.total_seconds(),
                        }
                    )
                )
                f.write("\n")
                f.write(
                    json.dumps(
                        {
                            "from_type": "xml",
                            "from": "files",
                            "to": "records",
                            "from_count": len(list(self.config.oaipmh_xml_files)),
                            "to_count": len(_records),
                            "duration": duration.total_seconds(),
                        }
                    )
                )
                f.write("\n")

        logger.info(f"""Peak: {mapped[0][0]}""")

        if self.config.extract_fulltexts:
            # download pdf

            pdf_cache = (
                Path(
                    self.dl_manager.manual_dir
                    if (
                        self.dl_manager is not None
                        and self.dl_manager.manual_dir is not None
                    )
                    else self.cache_dir
                )
                .expanduser()
                .absolute()
                .joinpath("pdf")
            )

            pdf_cache.mkdir(parents=True, exist_ok=True)

            self.pdf_cache = pdf_cache
            start_time = datetime.now()
            downloaded_pdfs = datasets.utils.py_utils.map_nested(
                self.get_pdf,
                _records,
                num_proc=16,
                desc=f"Download PDFs",
                disable_tqdm=not datasets.utils.logging.is_progress_bar_enabled(),
            )

            duration = datetime.now() - start_time

            logger.warning(
                f"""Downloaded {len(downloaded_pdfs)} files for {len(_records)} records in {duration.total_seconds()} s."""
            )

            if self.config.time_log is not None:
                with open(self.config.time_log, "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "from_type": "records",
                                "from": "records",
                                "to": "pdfs",
                                "from_count": len(list(_records)),
                                "to_count": len(downloaded_pdfs),
                                "duration": duration.total_seconds(),
                            }
                        )
                    )
                    f.write("\n")

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "records": _records[
                        : -(self.config.size if self.config.size else 100)
                    ]
                },
            ),  # FIXME
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={
                    "records": _records[
                        -(self.config.size if self.config.size else 100) :
                    ]
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "records": _records[: self.config.size if self.config.size else 100]
                },
            ),  # FIXME
        ]

    def get_pdf(self, record_dict):
        filename = self.pdf_cache.joinpath(f"{record_dict['id']}.pdf")
        try:
            link = _get_largest_pdf_url(
                get_pdf_links(
                    record_dict,  # pyright: ignore [reportGeneralTypeIssues] # str can be assigned to Text...
                    publisher=self.config.publisher,
                )
            )
        except ValueError as N:
            # raise UserWarning(f"No link for {record_dict['id']}") from N
            logger.error(f"No link for {record_dict['id']}: {N}")
            link = False

        if link and not filename.exists():
            with open(filename, "wb") as f:
                try:
                    f.write(requests.get(link).content)
                except Exception as N:
                    raise UserWarning(
                        f"An exception occureed when saving {link} as {filename}"
                    ) from N

        return str(filename)

    def _autolabel_and_identify(self, input) -> tuple[list[str], list[str], list[str]]:
        if input == []:
            return [], [], []

        assert (
            self.config.gazetteers is not None
        ), "Labeling is not supported without gazetteers"
        if isinstance(input, list) and any(isinstance(elem, str) for elem in input):
            l = [(i, None, None) for i in input]
            assert self.config.gazetteers is not None
            for key in self.config.gazetteers:
                l: list[tuple[list[str], list[str], list[str]]] = [
                    matching_and_linking_BIO(
                        self.config.gazetteers[key], i, key, label=lbl, links=lnk
                    )
                    for (i, lbl, lnk) in l
                ]

            return zip(*l)

        i, lbl, lnk = input, None, None
        for key in self.config.gazetteers:
            i, lbl, lnk = matching_and_linking_BIO(
                self.config.gazetteers[key], i, key, label=lbl, links=lnk
            )

        if lbl is None or lnk is None:
            raise UserWarning("Something went really wrong")

        return i, lbl, lnk

    def _tokenize_and_tag_and_identify(self, key: str, string) -> dict:
        """Create a dictionary containing a list of tokens and lists of corresponding tags and identifiers

        Args:
            key (str): original key used for the string
            string (_type_): _description_

        Returns:
            dict: _description_
        """
        # TODO
        try:
            _tokens, _tags, _links = self._autolabel_and_identify(string)
        except Exception as N:
            logger.error(f'Could not handle {string}: "{N}" occured')
            _tokens, _tags, _links = None, None, None

        return {
            f"{key}_tokens": _flatten(_tokens) or [],
            f"{key}_ner_tags": _flatten(_tags) or [],
            f"{key}_ner_links": _flatten(_links) or [],
        }

    def _parse_single_record(
        self,
        record_dict: OAIXMLRecordDict,
        # record
    ) -> dict[str, Any]:  # TODO Define dict properly
        """Parse a record to the feature specification

        Args:
            record_dict (OAIXMLRecordDict): Dict containing the data of an OAI PMH record

        Returns:
            dict[str, Any]: Entry matching the defined features
        """
        _record_dict = dict()
        # logger.warning(record_dict)
        for key in record_dict.keys():
            if key not in [
                "identifiers",
                "id",
                "subject",
                "relations",
                "id_",
                "pdf_links",
            ]:
                _record_dict.update(
                    self._tokenize_and_tag_and_identify(key, record_dict[key])
                    if self.config.do_string_match
                    else {key: record_dict[key]}
                )
            elif key in [
                "subject"
            ]:  # Special handling because it might be a list of lists
                _record_dict.update(
                    self._tokenize_and_tag_and_identify(
                        key,
                        record_dict[key]
                        # ", ".join(record_dict[key]) # TODO is this join really needed
                    )
                    if self.config.do_string_match
                    else {key: record_dict[key]}
                )
            elif key in ["id"]:
                _record_dict.update({key: str(record_dict[key])})
            else:
                _record_dict.update({key: record_dict[key]})

        if self.config.extract_fulltexts:
            start_time = datetime.now()

            try:
                filename = self.get_pdf(record_dict)
                if filename:
                    text = get_text_from_pdf(filename)
                else:
                    text = ""

            except Exception as N:
                logger.warning(f"Error extracting text for {record_dict['id']}")
                text = ""
            duration = datetime.now() - start_time

            logger.warning(f"Extracted {len(text)} chars in {duration} s")
            if self.config.time_log is not None:
                with open(self.config.time_log, "a") as f:
                    f.write(
                        json.dumps(
                            {
                                "from_type": "pdf",
                                "from": record_dict["id"],
                                "to": "characters",
                                "from_count": 1,
                                "to_count": len(text),
                                "duration": duration.total_seconds(),
                            }
                        )
                    )
                    f.write("\n")

            key = "text"
            _record_dict.update(
                self._tokenize_and_tag_and_identify(key, text)
                if self.config.do_string_match
                else {key: [text]}
            )

        # merge fields

        _record_dict.update(
            {
                f"all{suffix}": [
                    *(_record_dict[f"title{suffix}"]),
                    *(_record_dict[f"subject{suffix}"]),
                    *(_record_dict[f"description{suffix}"]),
                    *(
                        _record_dict[f"text{suffix}"]
                        if self.config.extract_fulltexts
                        else []
                    ),
                ]
                for suffix in (
                    ["_tokens", "_ner_tags", "_ner_links"]
                    if self.config.do_string_match
                    else [""]
                )
            }
        )

        return _record_dict

    def _generate_examples(self, records: list[OAIXMLRecordDict]):
        """This function returns the examples in the raw (text) form."""

        start_time = datetime.now()
        _records = datasets.utils.py_utils.map_nested(
            self._parse_single_record,
            records,
            num_proc=16,
            desc="Parsing records",
            disable_tqdm=not datasets.utils.logging.is_progress_bar_enabled(),
        )
        duration = datetime.now() - start_time

        logger.warning(
            f"""Parsed {len(_records)} records in {duration.total_seconds()}s."""
        )
        if self.config.time_log is not None:
            with open(self.config.time_log, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "from_type": "records",
                            "from": "records",
                            "to": "records",
                            "from_count": len(records),
                            "to_count": len(_records),
                            "duration": duration.total_seconds(),
                        }
                    )
                )
                f.write("\n")

        for _record_dict in _records:
            yield _record_dict["id_"], _record_dict
