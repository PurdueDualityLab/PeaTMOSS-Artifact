import sqlite3
from os.path import abspath
from pathlib import Path
from sqlite3 import Connection
from typing import List

import click
import pandas
from pandas import DataFrame


def postProcess(df: DataFrame) -> DataFrame:
    df.drop(
        labels=[
            "owner",
            "name",
            "model_hub_id",
            "sha",
            "downloads",
            "likes",
            "has_snapshot",
            "ptm_issues_id",
            "ptm_pull_requests_id",
        ],
        axis=1,
        inplace=True,
    )

    df.rename(
        columns={
            "url": "Project URL",
            "context_id": "Model Name",
            "repo_url": "Model URL",
        },
        inplace=True,
    )

    return df


def mergeTables(
    models: DataFrame, projects: DataFrame, modelProjectPairs: DataFrame
) -> DataFrame:
    projects.rename(columns={"id": "reuse_repository_id"}, inplace=True)
    models.rename(columns={"id": "model_id"}, inplace=True)

    foo: DataFrame = projects.merge(
        right=modelProjectPairs,
        how="left",
        on="reuse_repository_id",
    )

    bar: DataFrame = foo.merge(right=models, how="left", on="model_id")

    return bar


def loadTable(table: str, con: Connection) -> DataFrame:
    query: str = "SELECT * FROM {}"
    df: DataFrame = pandas.read_sql_query(sql=query.format(table), con=con)
    return df


@click.command()
@click.option(
    "-d",
    "--db",
    default="../../data/PeaTMOSS.db",
    type=Path,
    help="Path to PeaTMOSS to analyze",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    default="../../data/mapping/ghRepo_to_ptmProject.json",
    type=Path,
    help="Path to store application output",
    show_default=True,
)
def main(db: Path, output: Path) -> None:
    dbFilepath: Path = Path(abspath(db))
    outputFilepath: Path = Path(abspath(output))

    print(f"Reading data from {dbFilepath}...")

    con: Connection = sqlite3.connect(database=dbFilepath)

    models: DataFrame = loadTable(table="model", con=con)
    projects: DataFrame = loadTable(table="reuse_repository", con=con)
    modelProjectPairs: DataFrame = loadTable(table="model_to_reuse_repository", con=con)

    con.close()

    df: DataFrame = mergeTables(
        models=models,
        projects=projects,
        modelProjectPairs=modelProjectPairs,
    )

    foo: DataFrame = postProcess(df=df)

    print(f"Writing data to {outputFilepath}...")
    foo.T.to_json(path_or_buf=outputFilepath, indent=4, index=False)


#   baz: List[str] = []
#    bar: List[str] = foo["Project URL"].to_list()

#    url: str
#    for url in bar:
#        splitURL: List[str] = url.split(sep="/")
#        author: str = splitURL[-2]
#        repo: str = splitURL[-1]
#        baz.append(f"{author}_{repo}\n")

#     baz = sorted(baz)
#     with open(file="mappedGitHubProjects.txt", mode="w") as mgp:
#         mgp.writelines(baz)
#         mgp.close()


if __name__ == "__main__":
    main()
