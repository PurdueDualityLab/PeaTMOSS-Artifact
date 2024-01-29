from ModelHubClass import ModelHubClass
import petl as etl
from petl import Table
import logging
from typing import List, Mapping

class TFModelGarden(ModelHubClass):
    def __init__(self):
        self.name = "HuggingFace"
        self.data_path = "/scratch/bell/jone2078/PTMTorrent/ptm_torrent/huggingface/data"
        self.transformed_data = {}        
        self.transformed_data["model_hub"] = etl.fromcolumns([['url', 'name'],
                                              ['https://huggingface.co/models', 'HuggingFace']])
