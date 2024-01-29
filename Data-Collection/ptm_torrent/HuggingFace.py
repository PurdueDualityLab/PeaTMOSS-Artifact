from ModelHubClass import ModelHubClass
from huggingface_hub import HfApi, snapshot_download
from huggingface_hub.hf_api import ModelInfo, DatasetInfo
import shutil
from sys import argv
from itertools import chain

import logging
import petl as etl
from petl import Table
from collections import OrderedDict
from typing import List, Mapping

def wrap_in_list(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]

def non_null_vals(obj):
    return [val for val in wrap_in_list(obj) if val is not None]

SCRATCH_DIR = "/scratch/bell/jone2078"
CACHE_DIR = f"{SCRATCH_DIR}/huggingface_cache"
DATA_DIR = f"{SCRATCH_DIR}/huggingface_data"
# HuggingFace extends ModelHubClass in order to provide a class base for the HuggingFace API
class HuggingFace(ModelHubClass):
    api: HfApi = HfApi()
    models: Table
    datasets: Table

    # model_constraints and dataset_constraints provide the tests
    # that are run on the model and dataset metadata obtained from
    # the HF API to ensure that the metadata is valid
    model_constraints : list[dict] = [
        dict(name="modelId exists", field="modelId", test=str),
        dict(name="sha exists", field="sha", test=str),
        dict(name="lastModified exists", field="lastModified", test=str),
        dict(name="tags exists", field="tags", test=list),
        dict(name="pipeline_tag exists", field="pipeline_tag", test=bool),
        dict(name="siblings exists", field="siblings", test=list),
        dict(name="private exists", field="private", test=bool),
        dict(name="author exists", field="author", test=str),
        dict(name="config exists", field="config", test=dict),
        dict(name="securityStatus exists", field="securityStatus", test=str),
        dict(name="_id exists", field="_id", test=str),
        dict(name="id exists", field="id", test=str),
        dict(name="cardData exists", field="cardData", test=dict),
        dict(name="likes exists", field="likes", test=int),
        dict(name="downloads exists", field="downloads", test=int),
        dict(name="library_name exists", field="library_name", test=str),
        dict(name="modelId and id are equivalent", test=lambda row: row["modelId"] == row["id"]),
    ]

    dataset_constraints : list[dict] = [
        dict(name="id exists", field="id", test=str),
        dict(name="sha exists", field="sha", test=str),
        dict(name="lastModified exists", field="lastModified", test=str),
        dict(name="tags exists", field="tags", test=list),
        dict(name="private exists", field="private", test=bool),
        dict(name="author exists", field="author", test=str),
        dict(name="description exists", field="description", test=str),
        dict(name="citation exists", field="citation", test=str),
        dict(name="cardData exists", field="cardData", test=dict),
        dict(name="siblings exists", field="siblings", test=list),
        dict(name="_id exists", field="_id", test=str),
        dict(name="disabled exists", field="disabled", test=bool),
        dict(name="gated exists", field="gated", test=bool),
        dict(name="likes exists", field="likes", test=int),
        dict(name="downloads exists", field="downloads", test=int),
        dict(name="paperswithcode_id exists", field="paperswithcode_id", test=str),
    ]

    # model_headers and dataset_headers provide the headers for the
    # model and dataset metadata tables
    model_headers : tuple = (
        "modelId",
        "sha",
        "lastModified",
        "tags",
        "pipeline_tag",
        "siblings",
        "private",
        "author",
        "config",
        "securityStatus",
        "_id",
        "id",
        "cardData",
        "likes",
        "downloads",
        "library_name",
    )

    dataset_headers : tuple = (
        "id",
        "sha",
        "lastModified",
        "tags",
        "private",
        "author",
        "description",
        "citation",
        "cardData",
        "siblings",
        "_id",
        "disabled",
        "gated",
        "likes",
        "downloads",
        "paperswithcode_id",
    )


    def __init__(self):
        self.name = "HuggingFace"
        self.data_path = "/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data"
        self.transformed_data = {}
        self.transformed_data["model_hub"] = etl.fromcolumns([['url', 'name'],
                                              ['https://huggingface.co/models', 'HuggingFace']])


    def extract(self, amount: int|None = 1000):
        raw_models: list[ModelInfo] = self.api.list_models(limit=amount,
                                                           full=True,
                                                           cardData=True,
                                                           fetch_config=True,
                                                           sort="downloads",
                                                           direction=-1)
        dict_models = []
        model: self.api.ModelInfo
        for model in raw_models:
            model = model.__dict__
            model["siblings"] = [sibling.__dict__ for sibling in model["siblings"]
                                 if "config" in sibling.rfilename and "json" in sibling.rfilename]
            dict_models.append(model)

        self.models = etl.fromdicts(dict_models)
        logging.warning(f"Found {etl.nrows(self.models)} models on HuggingFace API")
        logging.warning(f"Model Headers: {etl.header(self.models)}")

        raw_datasets: list[DatasetInfo] = self.api.list_datasets(limit=amount,
                                                                 full=True,
                                                                 sort="downloads",
                                                                 direction=-1)
        dict_datasets = [dataset.__dict__ for dataset in raw_datasets]

        for dataset in dict_datasets:
            dataset["siblings"] = [sibling.__dict__ for sibling in dataset["siblings"]
                                 if "config" in sibling.rfilename and "json" in sibling.rfilename] \
                                 if dataset["siblings"] else None

        self.datasets = etl.fromdicts(dict_datasets)
        logging.warning(f"Found {etl.nrows(self.datasets)} datasets on HuggingFace API")
        logging.warning(f"Dataset Headers: {etl.header(self.datasets)}")

    def verify_extraction(self):
        problems = etl.validate(self.models, constraints = self.model_constraints, header = self.model_headers)
        logging.warning(f"Total {self.name} model Errors: {problems.nrows()}")
        logging.debug(f"{self.name} model Errors:\n{problems.lookall()}")

        problems = etl.validate(self.datasets, constraints = self.dataset_constraints, header = self.dataset_headers)
        logging.warning(f"Total {self.name} dataset Errors: {problems.nrows()}")
        logging.debug(f"{self.name} dataset Errors:\n{problems.lookall()}")

    def downloadZipSnapshot(self, model_id: str, repo_type: str, zip: bool) -> str | None:
        destination_dir = f'{self.data_path}/{repo_type}/{model_id}'
        try:
            snapshot_dir = snapshot_download(model_id,
                                    repo_type=repo_type,
                                    cache_dir=CACHE_DIR,
                                    local_dir=f"{DATA_DIR}/{model_id}",
                                    local_dir_use_symlinks=False)
            snapshot_zip = shutil.make_archive(destination_dir, 'zip', snapshot_dir) if zip else snapshot_dir
        except Exception as e:
            print(f"An Exception occurred: {e}")
            snapshot_zip = e
        return snapshot_zip


    # Obtains relevant data from the extracted data through transformations
    # Should result in self.transformed_data having the tables created within DB_Schema.sql
    def transform(self):
        self.model_transform()
        self.dataset_transform()

    def model_transform(self):
        self.models = self.models.progress(50000, prefix="Unpacking CardData: ").unpackdict('cardData')
        self.models = self.models.progress(50000, prefix="Unpacking Config: ").unpackdict('config')
        self.models = self.models.progress(50000, prefix="Melting: ").melt('_id')
        self.models = self.models.progress(500000, prefix="Recasting: ").recast()
        self.models = self.models.progress(50000, prefix="Sorting: ").sort('downloads', reverse=True)
        print(self.models.header())

        model_mapping = OrderedDict()
        hf_tags = self.api.get_model_tags()
        # Model Table Fields
        model_mapping['context_id'] = 'modelId'
        model_mapping['model_hub'] = lambda row: self.name
        model_mapping['repo_url'] = lambda row: f"https://huggingface.co/{row['modelId']}"
        model_mapping['sha'] = 'sha'
        model_mapping['downloads'] = 'downloads'
        model_mapping['likes'] = 'likes'
        model_mapping['original_data'] = lambda row: row

        # Model Many to Many Fields
        model_mapping['architectures'] = lambda row: list(non_null_vals(row['architectures'] or [])) or []
        model_mapping['author'] = lambda row: list(set([row['author']])) or []
        model_mapping['datasets'] = lambda row: list(set(non_null_vals(row['datasets'] or []) + [tag for tag in row['tags'] or [] if tag in hf_tags.dataset.values()])) or []
        model_mapping['framework'] = lambda row: list(set(row['model_type'])) or []
        model_mapping['language'] = lambda row: list(set(non_null_vals(row['language'] or []) + [tag for tag in row['tags'] or [] if tag in hf_tags.language.values()])) or []
        model_mapping['library'] = lambda row: list(set(row['library_name'] + [tag for tag in row['tags'] or [] if tag in hf_tags.library.values()])) or []
        model_mapping['license'] = lambda row: list(set(non_null_vals(row['license'] or []) + [tag for tag in row['tags'] or [] if tag in hf_tags.license.values()])) or []
        model_mapping['paper'] = lambda row: non_null_vals([f"https://arxiv.org/abs/{tag.replace('arxiv:','')}" for tag in (row['tags'] or []) if 'arxiv:' in tag] or [])
        model_mapping['tags'] = lambda row: list(set([tag for tag in chain.from_iterable(non_null_vals(row['tags'] or []))
                                             if ":" not in tag and
                                                tag not in hf_tags.dataset.values() and
                                                tag not in hf_tags.language.values() and
                                                tag not in hf_tags.library.values() and 
                                                tag not in hf_tags.license.values() and
                                                tag is not None
                                                ] + non_null_vals(row['pipeline_tag'] or []))) or []
        model_mapping['datasets'] = lambda row: list(set(non_null_vals(row['datasets'] or []) + [tag for tag in row['tags'] or [] if tag in hf_tags.dataset.values()])) or []


        self.transformed_data["model"] = etl.fieldmap(self.models, (model_mapping))
        # print(etl.look(self.transformed_data["full"].cut(["context_id", "tags"]).select(lambda row: row["tags"] is None)))
        # temp = self.transformed_data["full"].select(lambda row: row["tags"] is None).values("context_id").list()
        # print(etl.look(self.models.cut(["modelId", "tags"]).select(lambda row: row["modelId"] in temp)))
        # self.transformed_data["model"] = etl.cut(self.transformed_data["full"], ['context_id', 'model_hub', 'sha', 'repo_url', 'original_data', 'downloads', 'likes'])
        # attribute_tables = ["tags", "architectures", "author", "datasets", "framework", "language", "library", "license"]
        # for table_name in attribute_tables:
        #     print(f"Generating {table_name} and model_to_{table_name} tables")
        #     self.transformed_data[table_name] = self.gen_attribute_table(self.transformed_data["full"].progress(50000, prefix=f"Attribute Table {table_name}: "), table_name)
        #     print(etl.look(self.transformed_data[table_name]))
        #     self.transformed_data[f"model_to_{table_name}"] = self.gen_junction_table(self.transformed_data["full"].progress(50000, prefix=f"Junction Table model_to_{table_name}: "), "context_id", table_name)
        #     print(etl.lookall(self.transformed_data[f"model_to_{table_name}"]))

    def gen_attribute_table(self, table: Table, field: str) -> Table:
        non_null_vals = [val for val in list(etl.values(table, field)) if val is not None]
        unique_vals = set([val for val in chain.from_iterable(non_null_vals)])
        new_table : Table = etl.fromcolumns([[val for val in unique_vals]], header=[field])
        return new_table

    def gen_junction_table(self, table: Table, left_field: str, right_field: str) -> Table:
        subset_table = etl.cut(table, left_field, right_field)
        longest_list = max([len(val) for val in list(etl.values(subset_table, right_field)) if val is not None])
        unpacked_table = etl.unpack(subset_table, right_field, [" "]*longest_list, include_original=False)
        melted_table = etl.melt(unpacked_table, left_field, valuefield=right_field).select(lambda row: row[right_field] is not None and row[left_field] is not None)
        junction_table = etl.cut(melted_table, [left_field, right_field])
        return junction_table

    def dataset_transform(self):
        self.datasets = self.datasets.progress(50000, prefix="Unpacking CardData: ").unpackdict('cardData')
        self.datasets = self.datasets.progress(50000, prefix="Melting: ").melt('id')
        self.datasets = self.datasets.progress(500000, prefix="Recasting: ").recast()
        self.datasets = self.datasets.progress(50000, prefix="Sorting: ").sort('downloads', reverse=True)

        dataset_mapping = OrderedDict()
        hf_tags = self.api.get_dataset_tags()
        # Dataset Table Fields
        dataset_mapping['context_id'] = 'id'
        dataset_mapping['model_hub'] = lambda row: self.name
        dataset_mapping['sha'] = 'sha'
        dataset_mapping['lastModified'] = 'lastModified'
        dataset_mapping['repo_url'] = lambda row: f"https://huggingface.co/datasets/{row['id']}"
        dataset_mapping['downloads'] = 'downloads'
        dataset_mapping['likes'] = 'likes'

        # Dataset Many to Many Fields
        dataset_mapping['tags'] = lambda row: set([tag for tag in row['tags']
                                             if ":" not in tag and tag not in hf_tags.language.values()] + \
                                            (row['task_categories'] or []) + \
                                            (row['size_categories'] or []) + \
                                            (row['annotations_creators'] or []) + \
                                            (row['language_creators'] or []) + \
                                            (row['annotation_creators'] or []))
        dataset_mapping['author'] = 'author'
        dataset_mapping['description'] = 'description'
        dataset_mapping['citation'] = 'citation'
        dataset_mapping['type'] = 'type'
        dataset_mapping['paperswithcode_id'] = 'paperswithcode_id'
        dataset_mapping['source'] = 'source_datasets'
        dataset_mapping['language'] = lambda row: (row['language'] or []) + (row['multilinguality'] or []) \
                                                  if row['language'] or row['multilinguality'] else []
        dataset_mapping['license'] = 'license'
        dataset_mapping['dataset_info'] = 'dataset_info'
        dataset_mapping['paper'] = lambda row: [f"https://arxiv.org/abs/{tag.replace('arxiv:','')}" for tag in row['tags'] if 'arxiv:' in tag] or None
        dataset_mapping['original_data'] = lambda row: row

        model_mapping['downloads'] = 'downloads'
        model_mapping['likes'] = 'likes'
        model_mapping['original_data'] = lambda row: row

        # Model Many to Many Fields
        model_mapping['architectures'] = lambda row: list(wrap_in_list(row['architectures'] or [])) or []
        model_mapping['author'] = lambda row: list(set([row['author']])) or []
        model_mapping['datasets'] = lambda row: list(set(wrap_in_list(row['datasets'] or []) + [tag for tag in row['tags'] or [] if tag in hf_tags.dataset.values()])) or []
        model_mapping['framework'] = lambda row: list(set(row['model_type'])) or []
        model_mapping['language'] = lambda row: list(set(wrap_in_list(row['language'] or []) + [tag for tag in row['tags'] or [] if tag in hf_tags.language.values()])) or []
        model_mapping['library'] = lambda row: list(set(row['library_name'] + [tag for tag in row['tags'] or [] if tag in hf_tags.library.values()])) or []
        model_mapping['license'] = lambda row: list(set(wrap_in_list(row['license'] or []) + [tag for tag in row['tags'] or [] if tag in hf_tags.license.values()])) or []
        model_mapping['paper'] = lambda row: [f"https://arxiv.org/abs/{tag.replace('arxiv:','')}" for tag in row['tags'] or [] if 'arxiv:' in tag] or []
        model_mapping['tags'] = lambda row: list(set([tag for tag in chain.from_iterable(non_null_vals(row['tags'] or []))
                                             if ":" not in tag and
                                                tag not in hf_tags.dataset.values() and
                                                tag not in hf_tags.language.values() and
                                                tag not in hf_tags.library.values() and 
                                                tag not in hf_tags.license.values() and
                                                tag is not None
                                                ] + wrap_in_list(row['pipeline_tag'] or []))) or []

        self.transformed_data["dataset"] = self.datasets.fieldmap(dataset_mapping)
        logging.warning(self.transformed_data["dataset"].header())

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    hf = HuggingFace()
    hf.extract(amount=None)
    hf.model_transform()
    hf.load_csv("")