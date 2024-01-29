import petl as etl
from huggingface_hub import HfApi, snapshot_download
import shutil
import logging
from sys import argv
from tqdm import tqdm

api = HfApi()
SCRATCH_DIR = "/scratch/bell/jone2078"
CACHE_DIR = f"{SCRATCH_DIR}/huggingface_cache"
DATA_DIR = f"{SCRATCH_DIR}/huggingface_data"

def downloadZipSnapshot(model_id: str, repo_type: str, zip: bool) -> str | None:
    try:
        snapshot_dir = snapshot_download(model_id,
                                repo_type=repo_type,
                                cache_dir=CACHE_DIR,
                                local_dir=f"{DATA_DIR}/{model_id}",
                                local_dir_use_symlinks=False)
        snapshot_zip = snapshot_dir
        # snapshot_zip = shutil.make_archive(destination_dir, 'zip', snapshot_dir) if zip else snapshot_dir
    except Exception as e:
        print(f"An Exception occurred: {e}")
        snapshot_zip = e
    return snapshot_zip

def downloadRepos(table):
    snapshots = {}
    commits = {}
    for row in tqdm(table.dicts()):

        snapshots[row['context_id']] = None # downloadZipSnapshot(row['context_id'], 'model', False)
        try:
            commit_info = [commit.__dict__ for commit in api.list_repo_commits(row['context_id'])]
            gitref_info = {key: [val.__dict__ for val in value] for key, value in api.list_repo_refs(row['context_id']).__dict__.items()}
            commits[row['context_id']] = {"commits": commit_info, "gitrefs": gitref_info}
        except Exception as e:
            commits[row['context_id']] = {"commits": [], "gitrefs": {}}

    table = table.addfields([("snapshot", lambda row: snapshots[row['context_id']]),
                             ("commits", lambda row: commits[row['context_id']])])
    return table


start = eval(argv[1])
end = start + 1
scale = 10000

logging.basicConfig(level=logging.INFO)

table = etl.fromcsv('/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data/csv/HF_model_slim.csv').rowslice(start * scale, end * scale)
table = downloadRepos(table)
table.tojson(f'/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data/json/snapshots/HF_model_{(start * scale)/1000}k-{(end * scale)/1000}k_snapshots.json', default=str)