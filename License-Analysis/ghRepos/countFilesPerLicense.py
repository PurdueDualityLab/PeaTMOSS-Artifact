from json import load
from os import listdir
from os.path import abspath
from pathlib import Path
from pprint import pprint
from typing import Any, List

import click
import pandas
from pandas import DataFrame
from progress.bar import Bar

# IGNORE_FILE_PATTERNS: str = ".py|.sh|.html|.js|.pdf|Dockerfile|.tex|.pkl|.tar"
CONDIENCE_THRESHOLD: int = 98


def loadJSONFile(filepath: Path) -> DataFrame | None:
    with open(file=filepath, mode="r") as jsonFile:
        json: dict[str, Any] = load(jsonFile)
        jsonFile.close()

    relevantJSON: dict[str, Any] = json["files"]
    df: DataFrame = DataFrame.from_records(data=relevantJSON)

    df.drop(
        columns=df.columns.difference(
            other=[
                "path",
                "detected_license_expression",
                "percentage_of_license_text",
            ]
        ),
        axis=1,
        inplace=True,
    )

    df["project"] = filepath.stem

    try:
        df: DataFrame = df[
            df["percentage_of_license_text"] >= CONDIENCE_THRESHOLD
        ].reset_index(drop=True)
    except KeyError:
        return None

    return df


def printFilenames(df: DataFrame) -> None:
    pathStrs: List[str] = df["path"].to_list()
    paths: List[Path] = [Path(p) for p in pathStrs]

    filenames: List[str] = [p.name for p in paths]

    pprint(filenames)


@click.command()
@click.option(
    "-d",
    "--dir",
    default="../../data/licenses/ghLicenses",
    type=Path,
    help="Path to directory containing individual repository license analysis from scancode to analyze",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    default="../../data/licenses/ghRepoLicenses.json",
    type=Path,
    help="Path to store application output",
    show_default=True,
)
def main(dir: Path, output: Path) -> None:
    dirFilepath: Path = Path(abspath(dir))
    outputFilepath: Path = Path(abspath(output))

    print(f"Reading data from {dirFilepath}...")

    dfs: List[DataFrame] = []
    files: List[Path] = [Path(dirFilepath, file) for file in listdir(path=dirFilepath)]

    with Bar(message="Loading JSON data... ", max=len(files)) as bar:
        file: Path
        for file in files:
            dfs.append(loadJSONFile(filepath=file))
            bar.next()

    df: DataFrame = pandas.concat(objs=dfs, ignore_index=True)
    df.sort_values(by="project", axis=0, inplace=True, ignore_index=True)

    print(f"Writing data to {outputFilepath}...")
    df.T.to_json(path_or_buf=outputFilepath, indent=4)


if __name__ == "__main__":
    main()
