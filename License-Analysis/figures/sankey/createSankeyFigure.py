from typing import Any, List

import click
import matplotlib.pyplot as plt
import pandas
from pandas import DataFrame
from plotly import graph_objects as go
from sankey_lib import sankey


def createFigure(data: dict[str, List[Any]], output: str) -> None:
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    # x = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    # y = [2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=data["label"],
                ),
                link=data,
            )
        ]
    )

    fig.update_layout(title_text="HF License to GH License Mapping", font_size=10)
    fig.write_image(output)


def preprocessData(df: DataFrame, dropNone: bool) -> dict[str, List[Any]]:
    if dropNone:
        df.dropna(inplace=True, ignore_index=True)
    else:
        df.fillna(value="no license", inplace=True)

    tempDF: DataFrame = (
        df[["HF License", "GH License"]].value_counts().reset_index(name="Count")
    )

    hfLicenses: List[str] = tempDF["HF License"].to_list()
    ghLicenses: List[str] = tempDF["GH License"].to_list()

    uniqueHFLicenses: List[str] = tempDF["HF License"].drop_duplicates().to_list()
    uniqueGHLicenses: List[str] = tempDF["GH License"].drop_duplicates().to_list()

    hfLicenseIndices: List[int] = [
        uniqueHFLicenses.index(hfLicense) for hfLicense in hfLicenses
    ]
    ghLicenseIndices: List[int] = [
        uniqueGHLicenses.index(ghLicense) for ghLicense in ghLicenses
    ]
    ghLicenseIndices = [
        i + len(uniqueHFLicenses) for i in ghLicenseIndices
    ]  # TODO: What does this do?

    labels: List[str] = uniqueHFLicenses + uniqueGHLicenses

    source: List[int] = hfLicenseIndices
    target: List[int] = ghLicenseIndices
    value: List[int] = tempDF["Count"].to_list()

    data: dict[str, List[Any]] = {
        "label": labels,
        "source": source,
        "target": target,
        "value": value,
    }

    return data


def plotPySankey(df: DataFrame) -> None:
    df.fillna(value="no license", inplace=True)
    foo: DataFrame = (
        df[["HF License", "GH License"]].value_counts().reset_index(name="Count")
    )

    sankey(
        left=foo["HF License"],
        right=foo["GH License"],
        leftWeight=foo["Count"],
        fontsize=12,
        spacer=0.05,
    )
    plt.gcf().set_size_inches(10, 5)
    plt.tight_layout()
    plt.savefig("test.pdf")


@click.command()
@click.option(
    "-d",
    "--data-filepath",
    required=True,
    type=str,
    help="Path to JSON data file to plot",
)
@click.option(
    "-o",
    "--output",
    default="sankey.pdf",
    type=str,
    help="Path to save figure to",
)
@click.option(
    "--drop-none",
    is_flag=True,
    show_default=True,
    default=False,
    type=bool,
    help="Drop projects that do not have a license",
)
def main(data_filepath: str, output: str, drop_none: bool) -> None:
    df: DataFrame = pandas.read_json(path_or_buf=data_filepath).T

    data: dict[str, List[Any]] = preprocessData(df=df, dropNone=drop_none)

    # createFigure(data=data, output=output)
    plotPySankey(df=df)


if __name__ == "__main__":
    main()
