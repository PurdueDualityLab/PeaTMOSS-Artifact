from json import load
from os.path import abspath
from pathlib import Path
from typing import Any, List

import click
import pandas
from pandas import DataFrame
from progress.bar import Bar


def loadJSONData(filepath: Path) -> List[dict[str, Any]]:
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


def constructDF(data: dict[str, Any], modelID: int) -> DataFrame | None:
    foo: dict[str, List[str | int]] = {}

    try:
        foo["domain"] = data["domain"]
    except TypeError:
        return None

    foo["modelID"] = [modelID] * len(foo["domain"])

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
    default="../../data/domains/ptmProjectDomains.json",
    type=Path,
    help="Path to output data from",
    show_default=True,
)
def main(input: Path, output: Path) -> None:
    inputFilepath: Path = Path(abspath(input))
    outputFilepath: Path = Path(abspath(output))

    print(f"Reading data from {inputFilepath}")
    dfList: List[DataFrame | None] = []

    models: List[dict[str, Any]] = loadJSONData(
        filepath=inputFilepath,
    )

    with Bar(message="Creating DataFrames... ", max=len(models)) as bar:
        model: dict[str, Any]
        for model in models:
            modelID: int = models.index(model)
            dfList.append(constructDF(data=model, modelID=modelID))
            bar.next()

    df: DataFrame = pandas.concat(objs=dfList, ignore_index=True)

    print(f"Writing data to {outputFilepath}")
    df.drop_duplicates(ignore_index=True).T.to_json(
        path_or_buf=outputFilepath,
        indent=4,
    )


if __name__ == "__main__":
    main()
