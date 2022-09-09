import re
import datasets
import typing
from typing import Union,List, Any
import os
from datasets.tasks.base import T
from numpy import record

import requests

from langcodes import Language
from collections.abc import Sequence
from pathlib import Path

from datasets.tasks import TextClassification

from itertools import chain
from datasets import logging

from .helpers import _get_largest_pdf_url, _flatten
from .extract_pdf import get_text_from_pdf
from .xml_loader import load_xml_file, OAIXMLLoader, OAIXMLRecordDict
from .gazetteer import read_gazetteer, Gazetteer
from .publishers import get_pdf_links

import json

from datetime import datetime

import pickle


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

from .dict_matcher import DictMatcher, matching_and_linking_BIO

from pathlib import Path


class OAIPMHConfig(datasets.BuilderConfig):
    def __init__(
        self,
        # citation,
        # url,
        publisher: str,
        extract_fulltexts: bool,# = False,
        do_string_match: bool,# = True,
        language: typing.Union[str,None] = "all",
        size: typing.Union[int,None] = None,
        label_classes=("False", "True"),
        token_label_classes: Union[List[str], None] = None,
        link_label_classes: Union[List[str], None] = None,
        labels: Union[Sequence[str],None] = None,
        gazetteers: Union[dict[str,Gazetteer],Gazetteer,None] = None,
        **kwargs,
    ):
        """BuilderConfig for OAIPMH



        Args:
        oai_xml_files: List of XML files in the OAI-PMH XML format


        language: str representing a language to restrict to or "all"
        extract_fulltexts: boolean specifying wether the texts should be extracted
        **kwargs: Arguments passed to the parent class
        """

        # TODO include OAI PMH url support and load with sickle

        super(OAIPMHConfig, self).__init__(**kwargs)

        self.publisher = publisher
        self.language = language
        self.extract_fulltexts = extract_fulltexts

        self.do_string_match = do_string_match

        self.size = size

        if labels == None:
            # TODO fix hardcoded values
            with open(Path("~/Documents/Bachelor_INF/src/rdf_labels.txt").expanduser()) as f:
                labels = f.read().splitlines()
        self.labels = labels


    
        if gazetteers == None:
            # TODO fix hardcoded paths
            gazetteers = {
                f"{'-'.join(p.stem.split('.'))}": read_gazetteer(p)
                for p in Path("~/Documents/Bachelor_INF/data/gazetteers")
                .expanduser()
                .glob("*.dict")
            }
        
        self.gazetteers = gazetteers

        if self.gazetteers == dict() and token_label_classes == None and link_label_classes == None:
            raise Exception("Empty gazetteers dicts and no token_label_classes and / or link_label_classes are defined")

        if token_label_classes == None:
            token_label_classes = [
                "O",
                *[f"I-{token_type.upper()}" for token_type in gazetteers.keys()],
                *[f"B-{token_type.upper()}" for token_type in gazetteers.keys()],
            ]
        
        self.token_label_classes = token_label_classes

        if link_label_classes == None:
            link_label_classes =['']+list({
                    link
                    for token_type in gazetteers.keys()
                    if (gazetteer:=gazetteers[token_type])
                    for entry in gazetteer
                    if (link:=gazetteer[entry])
                })

        self.link_label_classes = link_label_classes

        self.version = "0.3.1"

        self.publisher = publisher

        def __getstate__(self):
            state = self.__dict__.copy()

            del state['tokenizer']
            del state['_get_pdf_links']
            del state['matcher']
    
            return state

        def __setstate__(self, state):
            self.__dict__.update(state)

class OAIPMH(datasets.GeneratorBasedBuilder):

    VERSION = datasets.Version("2.4.0")

    PUBLISHER_DIR = "../../data/oaipmharvest/"

    # TODO use configurable publisher dir
    BUILDER_CONFIGS = [
        OAIPMHConfig(
            name=f"{publisher}{'_ft' if extract_fulltexts else ''}{'' if do_string_match else '_raw'}",
            publisher=publisher,
            do_string_match = do_string_match,
            extract_fulltexts= extract_fulltexts,
            # citation,
            # url
        )
        for extract_fulltexts in [True, False]
        for publisher in ["lang-sci-press", "ubffm"]
        for do_string_match in [True, False]
    ]

    _STRING_SEQUENCE = datasets.Sequence(datasets.Value("string"))

    _NER_TOKEN_SEQUENCE = datasets.Sequence(datasets.Value("string"))

    # _NER_TAG_SEQUENCE = datasets.Sequence(
    #     # datasets.Value("string")
    #     datasets.features.ClassLabel(
    #         names=self.config.token_label_classes
    #     )
    # )

    # _NER_LINK_SEQUENCE = datasets.Sequence(
    #     # datasets.Value("string")
    #     datasets.features.ClassLabel(
    #         names=self.config.link_label_classes
    #     )
    #     )

    @property
    def manual_download_instructions(self):
        return (
            "To use this dataset you need to provide at least a set of OAI-PMH XML-Files in a `xml` directory."
            "You can get those by using [oaipmharvest](https://github.com/ubffm/oaipmharvest)."
            "To use the string matching functionality you additionally need one or more gazetteers in a `gazetteers` directory"
            "The gazetteers are expected to be formatted as 'entry\tURI'"
        )


    def _info(self):

        features = dict()

        features["id_"] = datasets.Value("string")
        features["id"] = datasets.Value("string")
        features["identifiers"] = datasets.Sequence(feature=datasets.Value("string"))    
        features["relations"] = datasets.Sequence(feature=datasets.Value("string"))


        for field in ["all", "title", "subject", "description",
            *(
                ["text"] if self.config.extract_fulltexts else []
            )
        ]:
            if self.config.do_string_match:
                features[f"{field}_tokens"] = datasets.Sequence(datasets.Value("string"))
                features[f"{field}_ner_tags"] = datasets.Sequence(datasets.features.ClassLabel(names=self.config.token_label_classes))
                features[f"{field}_ner_links"] = datasets.Sequence(datasets.features.ClassLabel(names=self.config.link_label_classes))
            else:
                features[f"{field}"] = datasets.Sequence(datasets.Value("string"))

        # if self.config.extract_fulltexts:
        #     features["pdf_links"] = datasets.Sequence(feature=datasets.Value("string"))

        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(features),
            # TODO
            # No default supervised_keys (as we have to pass both question
            # and context as input).
            supervised_keys=None,
            homepage="https://rajpurkar.github.io/SQuAD-explorer/",  # FIXME
            citation=_CITATION,
            # TODO add task_templates
        )

    def _split_generators(
        self, dl_manager: datasets.DownloadManager
    ) -> Sequence[datasets.SplitGenerator]:
        # TODO use API directly, e.g. with sickle
        # TODO use streaming generator to load files only if needed

        # inspired by https://huggingface.co/datasets/matinf/blob/main/matinf.py#L134
        if dl_manager.manual_dir == None or not (data_dir := Path(dl_manager.manual_dir).expanduser().absolute()).exists():
            raise FileNotFoundError(
                f"""{data_dir if data_dir else 'data_dir'} does not exist. Make sure you insert a manual dir via `datasets.load_dataset('oaipmh', data_dir=...)` that includes an `xml` directory containing the OAI-PMH XML-Files. 
                A `gazetteers` directory containing the gazetteers is also required for the string matching functionality to work. Manual download instructions: {self.manual_download_instructions}"""
            )
        
        oaipmh_xml_files = data_dir.joinpath('xml').glob('*.xml')
        start_time = datetime.now()
        mapped = list(datasets.utils.py_utils.map_nested(
            load_xml_file,
            list(oaipmh_xml_files),
            num_proc=16,
            desc="Parsing XML files",
            disable_tqdm=not datasets.utils.logging.is_progress_bar_enabled(),   
        ))

        duration = datetime.now() - start_time

        _records = _flatten(mapped)

        if _records is None:
            raise Exception(f"Error handling the records")
        

        logger.warning(f"""Parsed {len(list(oaipmh_xml_files))} files to  {len(mapped)} lists containing {len(_records)} records in {duration.total_seconds()} s.
        Peak: {mapped[0][0]}
        """)
        
        if self.config.extract_fulltexts:
            # download pdf

            data_dir.joinpath("pdf").mkdir(exist_ok=True)

            start_time = datetime.now()
            downloaded_pdfs = datasets.utils.py_utils.map_nested(
                self.get_pdf,
                _records,
                num_proc=16,
                desc=f"Download PDFs",
                disable_tqdm=not datasets.utils.logging.is_progress_bar_enabled(),
            )
                    
            duration = datetime.now() - start_time

            logger.warning(f"""Downloaded {len(downloaded_pdfs)} files in {duration.total_seconds()} s.""")

        return [

            datasets.SplitGenerator(
                name=datasets.Split.TRAIN, gen_kwargs={
                "records": _records[:-(self.config.size if self.config .size else 100)]
                }
            ),  # FIXME
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION, gen_kwargs={
                    "records": _records[-(self.config.size if self.config.size else 100):]
                }
            ),           
            datasets.SplitGenerator(
                name=datasets.Split.TEST, gen_kwargs={
                    "records": _records[:self.config.size if self.config.size else 100]
                }
            ),  # FIXME
        ]

    def get_pdf(self, record_dict):

        if self.dl_manager.manual_dir is None:
            raise UserWarning(f"Usage error. {self.manual_download_instructions}")

        filename = Path(self.dl_manager.manual_dir).expanduser().absolute().joinpath("pdf").joinpath(f"{record_dict['id']}.pdf")
        try:
            link = _get_largest_pdf_url(
                get_pdf_links(record_dict,publisher = self.config.publisher)
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
                    raise UserWarning(f"An exception occureed when saving {link} as {filename}") from N

        return str(filename)
            
    def _autolabel(self, input) -> tuple[Sequence[str], Sequence[str]]:

        if isinstance(input, list):
            l = [self.matcher.categorize(self.tokenizer(i)) for i in input]
            return zip(*l)

        return self.matcher.categorize(self.tokenizer(input))

    def _autolabel_and_identify(self, input) -> tuple[list[str], list[str], list[str]]:
        if input == []:
            return [],[],[]

        if isinstance(input, list) and any(isinstance(elem, str) for elem in input):
            l = [(i, None, None) for i in input]
            for key in self.config.gazetteers:
                l: list[tuple[list[str], list[str], list[str]]] = [
                    matching_and_linking_BIO(
                        self.config.gazetteers[key], i, key, label=lbl, links=lnk
                    )
                    for (i, lbl, lnk) in l
                ]

            logger.debug(
                f"""
                Input: {input}

                Output: {l}

                Zip Output: {zip(*l)}
                """
            )
            return zip(*l)

        i, lbl, lnk = input, None, None
        for key in self.config.gazetteers:
            i, lbl, lnk = matching_and_linking_BIO(
                self.config.gazetteers[key], i, key, label=lbl, links=lnk
            )

        if (lbl, lnk) == (None, None):
            raise UserWarning("Something went really wrong")

        logger.info(
            f"""
                Input: {input}

                Output: {(i, lbl, lnk)}
                """
        )
        return i, lbl, lnk

    def _tokenize_and_tag(self, key, string):
        # TODO
        try:
            _tokens, _tags = self._autolabel(string)
        except Exception as N:
            logger.error(f"Could not handle {string}: {N} occured")
            raise Exception(f"Could not handle {string}") from N
            _tokens, _tags = ([],), ([],)

        return {
            f"{key}_tokens": _tokens[0] or [],
            f"{key}_ner_tags": _tags[0] or [],
        }




    def _tokenize_and_tag_and_identify(self, key: str, string) -> dict:
        # TODO
        try:
            _tokens, _tags, _links = self._autolabel_and_identify(string)
        except Exception as N:
            logger.error(f'Could not handle {string}: "{N}" occured')
            raise(N)
            _tokens, _tags, _links = None, None, None

        # def _flatten(
        #     input: typing.Union[None, list[typing.Union[typing.Any, list[typing.Any]]]]
        # ) -> typing.Union[None, list[typing.Any]]:
        #     if input is None:
        #         return None
        #     if any(isinstance(elem, list) for elem in input):
        #         return [subelem for elem in input for subelem in elem]
        #     return input

        return {
            f"{key}_tokens": _flatten(_tokens) or [],
            f"{key}_ner_tags": _flatten(_tags) or [],
            f"{key}_ner_links": _flatten(_links) or [],
        }


    def _parse_single_record(
        self,
        record_dict: OAIXMLRecordDict,
        #record
    ) -> dict[str, Any]: # TODO Define dict properly
        _record_dict = dict()
        # logger.warning(record_dict)
        for key in record_dict.keys():
            if key not in ["identifiers", "id", "subject","relations", "id_", "pdf_links"]:
                _record_dict.update(
                    self._tokenize_and_tag_and_identify(key, record_dict[key])
                    if self.config.do_string_match else 
                    { key: record_dict[key]}
                )
            elif key in ["subject"]:
                _record_dict.update(
                    self._tokenize_and_tag_and_identify(
                        key,
                        record_dict[key]
                        # ", ".join(record_dict[key]) # TODO is this join really needed
                    )
                if self.config.do_string_match else 
                    { key: record_dict[key]}
                )
            elif key in ["id"]:
                _record_dict[key] = str(record_dict[key])
            else:
                _record_dict[key] = record_dict[key]

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
            duration = datetime.now()-start_time

            logger.warning(f"Extracted {len(text)} chars in {duration} s")
            
            key = "text"
            _record_dict.update(
                    self._tokenize_and_tag_and_identify(key, text)
                    if self.config.do_string_match else 
                    { key: [ text ]}
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

    def _load_or_parse_and_load(
        self, file: typing.Union[str, bytes, os.PathLike]
    ) -> list[dict]:
        """
        This function loads the tagged CoNLL files,
        if they exist or creates them if they don't
        """

        _json_file = Path(self.cache_dir).joinpath(
            self.config.name, Path(file).with_suffix(".json").name
        )
        _json_file.parent.mkdir(exist_ok=True)

        try:
            with open(_json_file) as f:
                _records = json.load(f)

        except FileNotFoundError:
            records = load_xml_file(file)

            progress = logging.tqdm(
                unit="records",
                total=len(records),
                disable=not logging.is_progress_bar_enabled(),
            )
            successes = 0

            _records = []
            for (record_dict, record) in records:

                _records.append(
                    self._parse_single_record(
                    record_dict,
                    # record
                ))
                progress.update(1)
                successes += 1

            if len(records) != len(_records):
                logger.warning(
                    f"Not all records were properly handled: {len(records)-successes}/{len(records)}"
                )

            with open(_json_file, "w") as f:
                json.dump(_records, f)



        return _records

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

        logger.warning(f"""Parsed {len(_records)} records in {duration.total_seconds()}s.""")

        for _record_dict in _records:
            yield _record_dict["id_"], _record_dict



    def _generate_examples_old(self, files: list[typing.Union[str, bytes, os.PathLike]]):
        """This function returns the examples in the raw (text) form."""
        logger.info("generating examples from = %s", files)

        # with open(filepath) as f:
        # loader = OAIXMLLoader(files)  # FIXME

        # TODO add multiprocessing
        records = []
        progress = logging.tqdm(
            unit="files",
            total=len(files),
            disable=not logging.is_progress_bar_enabled(),
        )
        successes = 0
        for f in files:
            if self.config.do_string_match:
                records += self._load_or_parse_and_load(f)
            else:
                records += [ dict(r) for r,_ in  load_xml_file(f) ]

            progress.update(1)
            successes += 1

        if successes != len(files):
            logger.warning(
                f"Not all files were handled successfully: {len(files)-successes}/{len(files)}"
            )

        logger.info(f"Loaded {len(records)}")

        # id_, record = next(xmlloader)

        for _record_dict in records:
            if self.config.extract_fulltexts:
                # Doing this check here makes it easier to add partial support for other publishers
                #_record_dict["pdf_links"] = _get_pdf_links(record_dict)
                try:
                    _record_dict["pdf_links"] = get_pdf_links(_record_dict, publisher=self.config.publisher)
                except Exception as exc:
                    logger.warning(f"Exception occured when handling {_record_dict['id']}: {exc}")
                    _record_dict["pdf_links"] = []

                conllfilename = f"{_record_dict['id']}.conll.txt"
                filename = f"{_record_dict['id']}.pdf"

                if Path(conllfilename).is_file():
                    # TODO read conll file
                    pass
                
                else:
                    
                    try:
                        filename = self.get_pdf(_record_dict)

                        if Path(filename).is_file():

                            text = get_text_from_pdf(filename)

                        else:
                            logger.warning(f"No pdf files or links for {_record_dict['id']}")
                            text = ""

                    except Exception as N:
                        logger.warning(f"An exception occurred handling {_record_dict['id']}: {N}")
                        text = ""

                    if self.config.do_string_match:
                        _record_dict.update(self._tokenize_and_tag_and_identify("text", text))
                        # TODO save as f"{id}.conll.txt"

                    else:
                        _record_dict.update({"text": [ text ]})

   
            yield _record_dict["id_"], _record_dict