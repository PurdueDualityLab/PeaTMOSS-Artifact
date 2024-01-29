import time
from json import load
from json.decoder import JSONDecodeError
from os.path import abspath, isfile
from pathlib import Path
from typing import Any, List

import click
from huggingface_hub.repocard import ModelCard
from huggingface_hub.utils._errors import (EntryNotFoundError,
                                           RepositoryNotFoundError)
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get


def updateGHProjectLicense(df: DataFrame, data: dict[str, str | None]) -> None:
    keys: List[str] = list(data.keys())

    with Bar(message="Storing GitHub model licenses... ", max=len(keys)) as bar:
        key: str
        for key in keys:
            df["GH License"].where(
                df["GitHub Project URL"] != key, data[key], inplace=True
            )
            bar.next()


def updateHFModelLicense(df: DataFrame, data: dict[str, str | None]) -> None:
    keys: List[str] = list(data.keys())

    with Bar(message="Storing Hugging Face model licenses... ", max=len(keys)) as bar:
        key: str
        for key in keys:
            df["HF License"].where(
                df["Hugging Face Model ID"] != key, data[key], inplace=True
            )
            bar.next()


def identifyLicense_GH(projectURLs: Series, token: str) -> dict[str, str | None]:
    data: dict[str, str | None] = {}

    header: dict[str, str] = {"Authorization": f"Bearer {token}"}

    projectURLsList: List[str] = projectURLs.to_list()

    with Bar(
        message="Identifying the licenses of GitHub projects... ",
        max=len(projectURLsList),
    ) as bar:
        projectURL: str
        for projectURL in projectURLs:
            projectLicense: str | None = None
            splitURL: List[str] = projectURL.split("/")
            author: str = splitURL[-2]
            repo: str = splitURL[-1]

            apiURL: str = f"https://api.github.com/repos/{author}/{repo}"

            resp: Response = get(url=apiURL, headers=header)
            jsonResp: dict[str, Any] = resp.json()

            try:
                projectLicense = jsonResp["license"]["key"]
            except KeyError:
                projectLicense = None
            except TypeError:
                projectLicense = None

            data[projectURL] = projectLicense
            bar.next()

    return data


def identifyLicense_HF(modelIDs: Series) -> dict[str, str | None]:
    data: dict[str, str | None] = {}

    modelIDList: List[str] = modelIDs.to_list()

    with Bar(
        message="Identifying the licenses of Hugging Face models... ",
        max=len(modelIDList),
    ) as bar:
        modelID: str
        for modelID in modelIDList:
            try:
                card: ModelCard = ModelCard.load(repo_id_or_path=modelID)
                data[modelID] = card.data.get(key="license")
            except EntryNotFoundError:
                data[modelID] = None
            except RepositoryNotFoundError:
                data[modelID] = None
            bar.next()

    return data


def loadData(path: Path) -> DataFrame:
    data: List[List[str | None]] = []
    columns: List[str] = [
        "Hugging Face Model ID",
        "GitHub Project URL",
        "HF License",
        "GH License",
    ]

    with open(file=path) as jsonFile:
        try:
            jsonData: dict[str, Any] = load(jsonFile)
        except JSONDecodeError:
            jsonFile.close()
            print(f"{path} is not a valid JSON file")
            quit(1)
        jsonFile.close()

    modelIDs: List[str] = list(jsonData.keys())

    with Bar(
        message="Generating pairs of Hugging Face Model IDs and GitHub Project URLs... ",
        max=len(modelIDs),
    ) as bar:
        modelID: str
        for modelID in modelIDs:
            ghProjects: List[str] = jsonData[modelID]["usage_repository"]

            ghProject: str
            for ghProject in ghProjects:
                data.append([modelID, ghProject, None, None])

            bar.next()

    return DataFrame(data=data, columns=columns)


@click.command()
@click.option(
    "-d",
    "--data-filepath",
    required=True,
    type=str,
    help="Path to data file to analyze",
)
@click.option(
    "-t",
    "--gh-token",
    required=True,
    type=str,
    help="GitHub personal access token",
)
@click.option(
    "-o",
    "--json-output",
    required=True,
    type=str,
    help="Path to save JSON data",
)
def main(data_filepath: str, gh_token: str, json_output: str) -> None:
    dataPath: Path = Path(data_filepath)
    dataPath = Path(abspath(path=dataPath))

    try:
        assert isfile(path=dataPath)
    except AssertionError:
        print(f"{dataPath} is not a valid file path")
        quit(1)

    df: DataFrame = loadData(path=dataPath)
    hfModels: Series = df["Hugging Face Model ID"]
    ghProjects: Series = df["GitHub Project URL"]

    hfModelLicenses: dict[str, str | None] = identifyLicense_HF(modelIDs=hfModels)
    ghProjectLicenses: dict[str, str | None] = identifyLicense_GH(
        projectURLs=ghProjects,
        token=gh_token,
    )

    updateHFModelLicense(df=df, data=hfModelLicenses)
    updateGHProjectLicense(df=df, data=ghProjectLicenses)

    df.T.to_json(path_or_buf=json_output, indent=4)


if __name__ == "__main__":
    main()
