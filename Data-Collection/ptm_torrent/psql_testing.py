import psycopg2
import petl as etl
from petl import Table
from typing import List
import time

import psql
import json

JOIN_TABLE = 0
RECORD_TABLE = 1

postgres = psql.PSQL("LAPTOP-BAJPKPVL", "exampledb", "docker", "docker")

postgres.load_json("ptm_torrent/HuggingFace_model_1000000000-1000000000.json", ['model', 'model_hub'], RECORD_TABLE)


def _load_json__empty():

    pass

def _load_json__small():

    pass
