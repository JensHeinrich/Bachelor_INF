import typing
from typing import Union, TypeAlias

import os
from pathlib import Path

from numpy import isin

# from .dict_matcher import Gazetteer

Gazetteer: TypeAlias = dict[str, str]


def read_gazetteers(
    dir_or_files: Union[list[Union[str, Path]], Union[str, Path]]
) -> dict[str, Gazetteer]:
    """Create a dictionary of gazetteers from a directory

    Args:
        dir_or_files (Union[list[Union[str, Path]],Union[str, Path]]): directory or list of files to load

    Returns:
        dict[str, Gazetteer]: Dictonary containing the gazetteers
    """

    if isinstance(dir_or_files, list):
        gazetteer_files = [Path(p) for p in dir_or_files]
    else:
        gazetteer_files = Path(dir_or_files).expanduser().glob("*.dict")
    return {
        f"{'-'.join(p.stem.split('.'))}": read_gazetteer(p) for p in gazetteer_files
    }


def read_gazetteer(file: Union[str, Path]) -> Gazetteer:
    """Create Gazetteer from file

    Args:
        file (Union[str, Path]): File to read as Gazetteer

    Returns:
        Gazetteer: Contained Gazetteer
    """
    with open(file) as f:
        lines = f.readlines()

    return {
        split_line[0]: split_line[1]
        for line in lines
        if (split_line := line.strip().split("\t"))
    }


def write_gazetteer(file: Union[str, Path], gazetteer: Gazetteer):
    """Write a gazetteer to a file

    Args:
        file (Union[str,Path]): File to save the gazetteer as
        gazetteer (Gazetteer): Gazetteer to save
    """
    with open(file, "w") as f:
        f.write("\n".join([f"{k}\t{gazetteer[k]}" for k in gazetteer]))
