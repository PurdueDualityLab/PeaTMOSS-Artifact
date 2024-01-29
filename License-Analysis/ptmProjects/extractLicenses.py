import sqlite3
from os.path import abspath
from pathlib import Path
from sqlite3 import Connection

import click
import pandas
from pandas import DataFrame


def postProcess(df: DataFrame) -> DataFrame:
    df.drop(
        labels=[
            "license_id",
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
    return df.T


def mergeTables(
    models: DataFrame, licenses: DataFrame, modelLicensePairs: DataFrame
) -> DataFrame:
    licenses["name"].replace(to_replace="", value="None", inplace=True)
    licenses.rename(
        columns={"id": "license_id", "name": "license_name"},
        inplace=True,
    )

    models.rename(columns={"id": "model_id"}, inplace=True)

    foo: DataFrame = licenses.merge(
        right=modelLicensePairs,
        how="left",
        on="license_id",
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
    default="../../data/licenses/ptmProjectLicenses.json",
    type=Path,
    help="Path to store application output",
    show_default=True,
)
def main(db: Path, output: Path) -> None:
    dbFilepath: Path = Path(abspath(db))
    outputFilepath: Path = Path(abspath(output))

    print(f"Reading data from {dbFilepath}...")

    con: Connection = sqlite3.connect(database=db)

    models: DataFrame = loadTable(table="model", con=con)
    licenses: DataFrame = loadTable(table="license", con=con)
    modelLicensePairs: DataFrame = loadTable(table="model_to_license", con=con)

    con.close()

    df: DataFrame = mergeTables(
        models=models,
        licenses=licenses,
        modelLicensePairs=modelLicensePairs,
    )

    print(f"Writing data to {outputFilepath}...")
    postProcess(df=df).to_json(path_or_buf=output, indent=4)


if __name__ == "__main__":
    main()
