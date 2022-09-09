from gazetteer import read_gazetteer
from pathlib import Path

assert read_gazetteer(Path("~/Documents/Bachelor_INF/data/gazetteers/de.bll.dict").expanduser())['Abkürzung'] == 'http://data.linguistik.de/bll/bll-ontology#bll-133075222', "Unexpected value"
