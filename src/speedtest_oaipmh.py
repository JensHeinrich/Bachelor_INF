import json
from datetime import datetime
from pathlib import Path

import evaluate

import datasets
from datasets import load_dataset
from oaipmh.gazetteer import read_gazetteers
from oaipmh.helpers import (_flatten, get_link_label_classes_from_gazetteers,
                            get_token_label_classes_from_gazetteers)

#datasets.utils.logging.disable_progress_bar()

gazetteers = read_gazetteers("~/Documents/Bachelor_INF/data/tmp_dataset/gazetteers")
distribution = evaluate.load("label_distribution")


timings = []

for publisher, oaipmh_xml_files, extract_fulltexts, do_string_match in [
    (publisher, oaipmh_xml_files, extract_fulltexts, do_string_match)
    for (publisher, oaipmh_xml_files) in [
        (
            "ubffm",
            list(
                Path(
                    "~/Documents/Bachelor_INF/data/oaipmharvest/ubffm/ubffm-publikationen-linguistik/"
                )
                .expanduser()
                .absolute()
                .glob("*.xml")
            ),
        ),
        (
            "lang-sci-press",
            list(
                Path(
                    "~/Documents/Bachelor_INF/data/oaipmharvest/lang-sci-press/UNSPECIFIED-SET/"
                )
                .expanduser()
                .absolute()
                .glob("*.xml")
            ),
        ),
    ]
    for extract_fulltexts in [True, False]
    for do_string_match in [True, False]
]:
    start_time = datetime.now()

    dataset = load_dataset(
        "oaipmh",
        name=publisher,
        cache_dir=f"~/.cache/huggingface/datasets/SPEEDTEST/{publisher}{'_ft' if extract_fulltexts else ''}{'' if do_string_match else'_raw'}_debug",
        oaipmh_xml_files=oaipmh_xml_files,
        split="train",
        download_mode="force_redownload",
        #data_dir=f"~/Documents/Bachelor_INF/data/tmp_dataset_{publisher}{'_ft' if extract_fulltexts else ''}{'' if do_string_match else'_raw'}/",
        publisher="ubffm",
        extract_fulltexts=extract_fulltexts,
        do_string_match=do_string_match,
        gazetteers=gazetteers,
        token_label_classes=get_token_label_classes_from_gazetteers(gazetteers),
        link_label_classes=get_link_label_classes_from_gazetteers(gazetteers),
        time_log=f"~/Documents/Bachelor_INF/data/SPEEDTEST_oaipmh/{publisher}{'_ft' if extract_fulltexts else ''}{'' if do_string_match else'_raw'}_debug.json",
    )

    duration = datetime.now() - start_time

    timing = {
        "publisher": publisher,
        "oaipmh_xml_files": [str(f) for f in oaipmh_xml_files],
        "extract_fulltexts": extract_fulltexts,
        "do_string_match": do_string_match,
        "distribution_all_ner_tags": distribution.compute(
            data=(_flatten(dataset["all_ner_tags"]))
        )
        if do_string_match
        else tuple(),
        "tag_list": dataset.info.features["all_ner_tags"].feature.names,
        "distribution_all_ner_links": distribution.compute(
            data=_flatten(dataset["all_ner_links"])
        )
        if do_string_match
        else tuple(),
        "link_list": dataset.info.features["all_ner_links"].feature.names,
        "duration": duration,
    }

    print(timing)

    with open(
        f"SPEEDTEST_{publisher}{'_ft' if extract_fulltexts else ''}{'' if do_string_match else'_raw'}_debug.json",
        "w",
    ) as f:
        json.dump(timing, f)

    timings += [timing]

with open("SPEEDTEST_timings.json", "w") as f:
    json.dump(timings, f)
