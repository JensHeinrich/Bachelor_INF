import typing
from typing import Union

import os
from pathlib import Path

from .dict_matcher import Gazetteer

Gazetteer = dict[str, str]


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

def write_gazetteer(file: Union[str,Path], gazetteer: Gazetteer):
    """Write a gazetteer to a file

    Args:
        file (Union[str,Path]): File to save the gazetteer as
        gazetteer (Gazetteer): Gazetteer to save
    """
    with open(file, "w") as f:
        f.write(
                "\n".join([
                    f"{k}\t{gazetteer[k]}" 
                    for k in gazetteer
                    ])
            )
