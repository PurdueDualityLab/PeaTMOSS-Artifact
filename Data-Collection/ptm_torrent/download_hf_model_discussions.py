import petl as etl
from huggingface_hub import HfApi, snapshot_download
import shutil
import logging
from sys import argv
from tqdm import tqdm

import sys
import csv
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

api = HfApi()
SCRATCH_DIR = "/scratch/bell/jone2078"
CACHE_DIR = f"{SCRATCH_DIR}/huggingface_cache"
DATA_DIR = f"{SCRATCH_DIR}/huggingface_data"

def download_discussions(table):
    discussions = {}
    print("Downloading discussions")
    for row in tqdm(table.dicts()):
        try:
            disc_iterator = api.get_repo_discussions(row['context_id'])
            disc_details = [api.get_discussion_details(row['context_id'], disc.num).__dict__ for disc in disc_iterator]
            for discussion in disc_details:
                discussion["events"] = [event.__dict__ for event in discussion["events"]] 

            discussions[row['context_id']] = disc_details
        except Exception as e:
            print(e)
            discussions[row['context_id']] = []

    table = table.addfields([("discussions", lambda row: discussions[row['context_id']])] )
    return table


# table = etl.fromcsv('/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data/csv/HuggingFace_model_.csv')
# table = table.cut(['context_id', 'repo_url'])
# table.tocsv('/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data/csv/HF_model_slim.csv')
start = eval(argv[1])
end = start + 1
scale = 10000

logging.basicConfig(level=logging.INFO)
table = etl.fromcsv('/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data/csv/HF_model_slim.csv').rowslice(start * scale, end * scale)
table = download_discussions(table)
table.tojson(f'/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data/json/discussions/HF_model_{(start * scale)/1000}k-{(end * scale)/1000}k_discussions.json', default=str)