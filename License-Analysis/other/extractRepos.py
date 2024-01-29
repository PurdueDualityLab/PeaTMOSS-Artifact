from os.path import abspath
from pathlib import Path
from typing import List

import click
from progress.bar import Bar


def loadFiles(file: Path) -> List[str]:
    with open(file=file, mode="r") as dataFile:
        foo: List[str] = dataFile.readlines()
        dataFile.close()

    return foo


def identifyRepos(files: List[str]) -> None:
    f: str
    for f in files:
        fSplit: List[str] = f.strip().split(sep="/")
        print(f"{fSplit[0]}")


@click.command()
@click.option(
    "-f",
    "--file",
    required=True,
    type=str,
    help="Path to data file containing files captured within PeaTMOSS",
)
def main(file: str) -> None:
    fileDataPath: Path = Path(abspath(file))
    filesData: List[str] = loadFiles(file=fileDataPath)

    identifyRepos(files=filesData)


if __name__ == "__main__":
    main()
