from torch import hub
from ModelHubClass import ModelHubClass
from typing import List
from gql import gql, Client, transport
from gql.transport.aiohttp import AIOHTTPTransport
from queries import FILE_QUERY, GITHUB_TOKEN

import petl as etl
from petl import Table
import logging
import json
from collections import OrderedDict

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://api.github.com/graphql", 
                             headers={"Authorization": GITHUB_TOKEN,
                                      "Accept": "application/vnd.github.hawkgirl-preview+json"})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(FILE_QUERY)

variables = {
  "owner": "onnx",
  "name": "models"
}

class ONNXModelZoo(ModelHubClass):
    api: hub = hub
    models: Table

    model_headers : tuple = ('model',
    'model_path',
    'onnx_version',
    'opset_version',
    'extra_ports',
    'io_ports',
    'model_bytes',
    'model_sha',
    'model_with_data_bytes',
    'model_with_data_path',
    'model_with_data_sha',
    'tags'
    )

    model_constraints : List[dict] = [
        dict(name="model exists", field="model", test=str),
        dict(name="model_path exists", field="model_path", test=str),
        dict(name="onnx_version exists", field="onnx_version", test=str),
        dict(name="opset_version exists", field="opset_version", test=int),
        dict(name="model_sha exists", field="model_sha", test=str),
        dict(name="model_bytes exists", field="model_bytes", test=int),
        dict(name="tags exists", field="tags", test=list),
        dict(name="io_ports exists", field="io_ports", test=dict),
        dict(name="model_with_data_path exists", field="model_with_data_path", test=str),
        dict(name="model_with_data_sha exists", field="model_with_data_sha", test=str),
        dict(name="model_with_data_bytes exists", field="model_with_data_bytes", test=int),
    ]

    def __init__(self):
        self.name = "ONNXModelZoo"
        self.transformed_data = {}
        self.transformed_data["model_hub"] = etl.fromcolumns([['url', 'name'],
                                              ['https://github.com/onnx/models', self.name]])


    def extract(self):
        files = client.execute(query, variable_values=variables)
        json_file = [file["object"]["text"]
                     for file in files["repository"]["object"]["entries"]
                     if "ONNX_HUB_MANIFEST.json" in file["name"]][0]
        self.models = etl.fromdicts(json.loads(json_file.strip()))
        self.models = self.models.unpackdict("metadata")
        logging.info(f"Extracted {etl.nrows(self.models)} models from ONNXModelZoo")
        logging.debug(f"ONNXModelZoo headers: {etl.header(self.models)}")

    def verify_extraction(self):
        problems = etl.validate(self.models, constraints = self.model_constraints, header = self.model_headers)
        logging.info(f"Total {self.name} models with problems: {problems.nrows()}")
        logging.debug(f"{self.name} model Errors:\n{problems.lookall()}")

    def transform(self):
        model_mapping = OrderedDict()
        model_mapping['context_id'] = 'model_path'
        model_mapping['repo_url'] = lambda row: f"https://github.com/onnx/models/{row['model_path']}"
        model_mapping['sha'] = 'model_sha'
        model_mapping['tags'] = 'tags'
        model_mapping['library'] = lambda row: 'onnx'
        model_mapping['config_file'] = lambda row: (row['io_ports'] if row['io_ports'] else {}) | \
                                                   (row['extra_ports'] if row['extra_ports'] else {}) \
                                                   if row['io_ports'] or row['extra_ports'] else None

        self.transformed_data["model"] = etl.fieldmap(self.models, model_mapping)

        self.transformed_data["model_to_library"] = self.transformed_data["model"].cut('context_id', 'library')
        self.transformed_data["model_to_tag"] = self.transformed_data["model"].cut('context_id', 'tags')
        self.transformed_data["model_to_config"] = self.transformed_data["model"].cut('context_id', 'config_file')



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    onnx = ONNXModelZoo()
    onnx.extract()
    onnx.transform()
    onnx.frequency(onnx.transformed_data["model"])
