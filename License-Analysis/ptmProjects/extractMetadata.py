from json import load
from os.path import abspath
from pathlib import Path
from types import NoneType
from typing import Any, List

import click
import pandas
from pandas import DataFrame
from progress.bar import Bar

GOOD_COLUMNS: List[str] = [
    "domain",
    "frameworks",
    "libraries",
    "datasets",
    "license",
    "github_repo",
    "paper",
    "base_model",
    "parameter_count",
    "hardware",
    "hyper_parameters",
    "evaluation",
    "limitation_and_bias",
    "demo",
    "grant",
    "input_format",
    "output_format",
]


def loadJSONData(filepath: str) -> List[dict[str, Any]]:
    data: List[dict[str, Any]] = []

    with open(file=filepath, mode="r") as jsonFile:
        jsonData: dict[str, dict[str, Any]] = load(fp=jsonFile)
        jsonFile.close()

    modelKeys: List[str] = list(jsonData.keys())

    with Bar(message="Extracting data... ", max=len(modelKeys)) as bar:
        key: str
        for key in modelKeys:
            data.append(jsonData[key])
            bar.next()

    return data


def _countAny(test: Any) -> int:
    if bool(test):
        return 1
    else:
        return 0


def _countList(test: List[str]) -> int:
    val: str
    for val in test:
        if isinstance(val, str):
            if _countAny(val) == 1:
                return 1
        elif isinstance(val, dict):
            return _countDict(val)
        elif isinstance(val, list):
            return _countList(val)
        elif isinstance(val, int):
            return _countAny(val)
        elif isinstance(val, float):
            return _countAny(val)
        else:
            continue

    return 0


def _countDict(test: dict[str, Any]) -> int:
    keys: List[str] = list(test.keys())

    key: str
    for key in keys:
        if isinstance(test[key], str):
            if _countAny(test[key]) == 1:
                return 1
        elif isinstance(test[key], dict):
            return _countDict(test[key])
        elif isinstance(test[key], list):
            return _countList(test[key])
        else:
            continue
    return 0


def constructDF(data: dict[str, Any], modelID: int) -> DataFrame | None:
    taskList: List[str] = []

    try:
        rawTask: Any = data["model_task"]
    except TypeError:
        return None

    rawTaskList: List[str] = []
    if isinstance(rawTask, str):
        rawTaskList = [rawTask]
    else:
        rawTaskList = rawTask

    taskList: List[str] = []
    task: str
    for task in rawTaskList:
        if task.find(",") != -1:
            taskList.extend(
                [subtask.strip().replace(" ", "") for subtask in task.split(",")]
            )
        else:
            taskList.append(task)

    foo: dict[str, List[str | int]] = {"task": taskList}

    taskCount: int = len(foo["task"])
    foo["modelID"] = [modelID] * taskCount

    column: str
    for column in GOOD_COLUMNS:
        try:
            test: Any = data[column]
        except KeyError:
            foo[column] = [0] * taskCount
            continue

        if isinstance(test, str):
            foo[column] = [_countAny(test)] * taskCount

        elif isinstance(test, dict):
            foo[column] = [_countDict(test)] * taskCount

        elif isinstance(test, list):
            foo[column] = [_countList(test)] * taskCount

        elif isinstance(test, NoneType):
            foo[column] = [0] * taskCount
        else:
            foo[column] = [-1] * taskCount

    return DataFrame(data=foo)


@click.command()
@click.option(
    "-i",
    "--input",
    default="../../data/result_5000_10000.json",
    type=Path,
    help="Path to input data file to extract domains from",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    default="../../data/metadata/ptmProjectMetadata.json",
    type=Path,
    help="Path to output data from",
    show_default=True,
)
def main(input: Path, output: Path) -> None:
    dfList: List[DataFrame | None] = []
    inputFilepath: Path = Path(abspath(input))
    outputFilepath: Path = Path(abspath(output))

    print(f"Reading data from {inputFilepath}")

    models: List[dict[str, Any]] = loadJSONData(filepath=inputFilepath)

    with Bar(message="Creating DataFrames... ", max=len(models)) as bar:
        model: dict[str, Any]
        for model in models:
            modelID: int = models.index(model)
            dfList.append(constructDF(data=model, modelID=modelID))
            bar.next()

    df: DataFrame = pandas.concat(objs=dfList, ignore_index=True)

    print(f"Writing data to {outputFilepath}")
    df.T.to_json(path_or_buf=outputFilepath, indent=4)


if __name__ == "__main__":
    main()
