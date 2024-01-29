from os.path import abspath
from pathlib import Path
from typing import Hashable, List

import click
import pandas
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

GOOD_COLUMNS: List[str] = ["domain", "task_name", "reuse_repository_id"]


@click.command()
@click.option(
    "-m",
    "--mapping",
    default="../../data/mapping/ghRepo_to_ptmProject.json",
    type=Path,
    help="Path to GH Repo to PTM Project mapping file to analyze",
    show_default=True,
)
@click.option(
    "-t",
    "--tasks",
    default="../../data/tasks/ptmProjectTasks.json",
    type=Path,
    help="Path to PTM Project tasks file to analyze",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    default="../../data/mapping/ghRepo_to_ptmProject_tasks.json",
    type=Path,
    help="Path to store application output",
    show_default=True,
)
def main(mapping: Path, tasks: Path, output: Path) -> None:
    mappingFilepath: Path = Path(abspath(mapping))
    tasksFilepath: Path = Path(abspath(tasks))
    outputFilepath: Path = Path(abspath(output))

    print(f"Reading data from {mappingFilepath}...")
    projectPairings: DataFrame = pandas.read_json(path_or_buf=mappingFilepath).T

    print(f"Reading data from {tasksFilepath}...")
    ptmTasks: DataFrame = pandas.read_json(path_or_buf=tasksFilepath).T

    df: DataFrame = ptmTasks.merge(
        right=projectPairings,
        how="left",
        on="model_id",
    )
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    df.drop(
        labels=df.columns.difference(other=GOOD_COLUMNS),
        axis=1,
        inplace=True,
    )

    dfs: DataFrameGroupBy = df.groupby(by="task_name")

    dfList: List[DataFrame] = []
    foo: tuple[Hashable, DataFrame]
    for foo in dfs:
        bar: DataFrame = foo[1]
        bar.rename(columns={"reuse_repository_id": "project_count"}, inplace=True)
        projectCount: int = bar["project_count"].count()

        data: dict[str, List[str | int]] = {
            "domain": [bar["domain"].to_list()[0]],
            "project_count": [projectCount],
            "task_name": bar["task_name"].to_list()[0],
        }
        dfList.append(DataFrame(data=data))

    print(f"Writing data to {outputFilepath}...")
    pandas.concat(objs=dfList, ignore_index=True).T.to_json(
        path_or_buf=outputFilepath,
        indent=4,
    )


if __name__ == "__main__":
    main()
