from ModelHubClass import ModelHubClass
from ptm_torrent.utils.network import downloadJSON
from typing import List
from gql import gql, Client, transport
from gql.transport.aiohttp import AIOHTTPTransport
from queries import FILE_QUERY, GITHUB_TOKEN, CONFIG_QUERY

import json
import petl as etl
from petl import Table
import logging
from collections import OrderedDict

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://api.github.com/graphql", 
                             headers={"Authorization": GITHUB_TOKEN,
                                      "Accept": "application/vnd.github.hawkgirl-preview+json"})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)


class ModelHub(ModelHubClass):
    models: Table

    model_headers: tuple = (
        "id",
        "name",
        "task_extended",
        "github",
        "github_branch",
        "backend",
        "gpu",
    )

    model_constraints: List[dict] = [
        dict(name="id exists", field="id", test=str),
        dict(name="name exists", field="name", test=str),
        dict(name="task_extended exists", field="task_extended", test=str),
        dict(name="github exists", field="github", test=str),
        dict(name="github_branch exists", field="github_branch", test=str),
        dict(name="backend exists", field="backend", test=str),
        dict(name="gpu exists", field="gpu", test=str),
    ]

    def __init__(self) -> None:
        super()
        self.name = "ModelHub"
        self.transformed_data = {}        
        self.transformed_data["model_hub"] = etl.fromcolumns([['url', 'name'],
                                              ['https://github.com/modelhub-ai/modelhub', 'ModelHub']])

    def extract(self, amount: int = 10) -> None:
        variables = {
            "owner": "modelhub-ai",
            "name": "modelhub"
        }
        query = gql(FILE_QUERY)

        files = client.execute(query, variable_values=variables)
        json_file = [file["object"]["text"]
                     for file in files["repository"]["object"]["entries"]
                     if "models.json" in file["name"]][0]
        self.models = etl.fromdicts(json.loads(json_file.strip()))
        logging.warning(f"Found {etl.nrows(self.models)} models on ModelHub")
        logging.warning(f"Model Headers: {etl.header(self.models)}")


    def verify_extraction(self) -> None:
        problems = etl.validate(self.models, constraints = self.model_constraints, header = self.model_headers)
        logging.info(f"Found {problems.nrows()} problems with the extracted data")
        logging.debug(f"Problems\n: {problems.lookall()}")

    def transform(self) -> None:
        variables = {
            "owner": "",
            "name": ""
        }
        query = gql(CONFIG_QUERY)

        file_rows = []
        license_rows = []
        for row in etl.dicts(self.models):
            variables["owner"] = row["github"].split("/")[3]
            variables["name"] = row["github"].split("/")[4]
            print(variables)
            result = client.execute(query, variable_values=variables)
            file = result["repository"]["object"]["text"]
            license = result["repository"]["licenseInfo"]["key"] if result["repository"]["licenseInfo"] else None
            file_rows.append(json.loads(file.strip()))
            license_rows.append(license)
        
        self.models = self.models.addcolumn('license', license_rows)
        self.models = self.models.addcolumn('config', file_rows)
        self.models = self.models.unpackdict('config')
        self.models = self.models.unpackdict('meta')
        self.models = self.models.unpackdict('model')
        self.models = self.models.unpackdict('publication')

        model_mapping = OrderedDict()
        model_mapping['context_id'] = 'id'
        model_mapping['name'] = 'name'
        model_mapping['repo_url'] = 'github'
        model_mapping['library'] = lambda row: row['backend'] + \
                                    ([arch.strip() for arch in row['architecture'].split(',')] if row['architecture'] else []) + \
                                    ([row['format'].replace('.', '')] if row['format'] else [])
        model_mapping['author'] = lambda row: [author.strip() for author in row['authors'].split(',')]
        model_mapping['paper'] = 'url'
        model_mapping['config_file'] = 'io'
        model_mapping['datasets'] = 'data_source'
        model_mapping['license'] = 'license'
        model_mapping['tags'] = lambda row: ([row["learning_type"]] if row["learning_type"] else []) + \
                                            ([row["task"]] if row["task"] else []) + \
                                            ([row["task_extended"]] if row["task_extended"] else []) + \
                                            ([row["application_area"]] if row["application_area"] else []) + \
                                            ([row["data_type"]] if row["data_type"] else [])

        self.transformed_data["model"] = etl.fieldmap(self.models, model_mapping)

        self.transformed_data["model_to_tag"] = self.transformed_data["model"].cut('context_id', 'tags')
        self.transformed_data["model_to_paper"] = self.transformed_data["model"].cut('context_id', 'paper')
        self.transformed_data["model_to_license"] = self.transformed_data["model"].cut('context_id', 'license')
        self.transformed_data["model_to_author"] = self.transformed_data["model"].cut('context_id', 'author')
        self.transformed_data["model_to_library"] = self.transformed_data["model"].cut('context_id', 'library')
        self.transformed_data["model_to_config_file"] = self.transformed_data["model"].cut('context_id', 'config_file')


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    modelhub = ModelHub()
    modelhub.extract()
    modelhub.verify_extraction()
    modelhub.transform()
    modelhub.frequency(modelhub.models)