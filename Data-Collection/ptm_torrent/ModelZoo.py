from ModelHubClass import ModelHubClass
from ptm_torrent.utils.network import downloadJSON
from typing import List
from gql import gql, Client, transport
from gql.transport.aiohttp import AIOHTTPTransport
from queries import LICENSE_QUERY, GITHUB_TOKEN

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


class ModelZoo(ModelHubClass):
    url: str = "https://modelzoo.co/api/models/0/"
    headers: dict = {"User-Agent": "PTMTorrent", "Referer": "https://modelzoo.co/"}

    models: Table

    model_headers: tuple = (
        "slug",
        "title",
        "description",
        "stars",
        "link",
        "framework",
        "categories",
        "long_desc",
        "papers",
    )

    model_constraints: List[dict] = [
        dict(name="slug exists", field="slug", test=str),
        dict(name="title exists", field="title", test=str),
        dict(name="description exists", field="description", test=str),
        dict(name="stars exists", field="stars", test=int),
        dict(name="link exists", field="link", test=str),
        dict(name="framework exists", field="framework", test=str),
        dict(name="categories exists", field="categories", test=list),
        dict(name="long_desc exists", field="long_desc", test=str),
    ]

    def __init__(self) -> None:
        self.name = "ModelZoo"
        self.transformed_data = {}
        self.transformed_data["model_hub"] = etl.fromcolumns([['url', 'name'],
                                              ['https://modelzoo.co', self.name]])

    def extract(self, amount: int = -1) -> None:
        logging.info(f"Downloading JSON from {self.url}...")
        model_list = downloadJSON(self.url, self.headers)
        print(len(model_list["models"]))
        dict_models = []
        for model in model_list["models"][:]:
            model_url = f"https://modelzoo.co/api/models/{model['slug']}/"
            model_info = downloadJSON(model_url, self.headers)
            model["papers"] = model_info["papers"]
            dict_models.append(model)

        self.models = etl.fromdicts(dict_models)
        logging.info(f"Found {etl.nrows(self.models)} models on ModelZoo API")
        logging.debug(f"Model Headers: {etl.header(self.models)}")

    def verify_extraction(self) -> None:
        problems = etl.validate(self.models, constraints = self.model_constraints, header = self.model_headers)
        logging.info(f"Found {problems.nrows()} problems with the extracted data")
        logging.debug(f"Problems\n: {problems.lookall()}")

    def transform(self) -> None:
        variables = {
            "owner": "",
            "name": "",
        }
        query = gql(LICENSE_QUERY)

        license_rows = []
        for row in etl.dicts(self.models):
            variables["owner"] = row["link"].split("/")[3]
            variables["name"] = row["link"].split("/")[4]
            result = client.execute(query, variable_values=variables)
            license = result["repository"]["licenseInfo"]["key"] if result["repository"]["licenseInfo"] else None
            license_rows.append(license)
        
        self.models = etl.addcolumn(self.models, "license", license_rows)

        model_mapping = OrderedDict()
        model_mapping['context_id'] = 'slug'
        model_mapping['repo_url'] = 'link'
        model_mapping['likes'] = 'stars'
        model_mapping['framework'] = 'framework'
        model_mapping['license'] = 'license'
        model_mapping['tags'] = lambda row: [category["slug"] for category in row['categories']] \
                                             if row['categories'] else None
        model_mapping['paper'] = lambda row: [paper for paper in row["papers"].values()] \
                                             if row["papers"] else None
        
        self.transformed_data["model"] = etl.fieldmap(self.models, model_mapping)

        self.transformed_data["model_to_tag"] = self.transformed_data["model"].cut('context_id', 'tags')
        self.transformed_data["model_to_paper"] = self.transformed_data["model"].cut('context_id', 'paper')
        self.transformed_data["model_to_license"] = self.transformed_data["model"].cut('context_id', 'license')
        self.transformed_data["model_to_framework"] = self.transformed_data["model"].cut('context_id', 'framework')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    modelzoo = ModelZoo()
    modelzoo.extract()
    modelzoo.transform()
    modelzoo.frequency(modelzoo.models)