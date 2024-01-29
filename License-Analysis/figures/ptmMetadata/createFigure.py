from typing import Hashable, List

import matplotlib.pyplot as plt
import pandas
from matplotlib.colors import XKCD_COLORS
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

FONTSIZE: int = 12
X_COL: str = "tasks"
Y_COL: str = "count"


def main() -> None:
    modelTasks: List[str] = []
    counts: List[int] = []
    data: dict[str, List[str | int]] = {}

    df: DataFrame = pandas.read_json(
        path_or_buf="../../data/countMetadataPerPTM.json"
    ).T

    dfs: DataFrameGroupBy = df.groupby(by="task")

    foo: tuple[Hashable, DataFrame]
    for foo in dfs:
        foo[1].drop(columns=["task", "modelID"], inplace=True)
        count: float = foo[1].sum(axis=1).sum()

        modelTasks.append(str(foo[0]))
        counts.append(int(count))

    data[X_COL] = modelTasks
    data[Y_COL] = counts

    df: DataFrame = DataFrame(data=data)
    df = df[df[X_COL] != "pretraining"]
    df = df[df[X_COL] != "pre-training"]
    df.replace(
        to_replace="text2text-generation", value="text-to-text-generation", inplace=True
    )
    df.replace(to_replace="", value="none", inplace=True)
    df.sort_values(by="count", axis=0, ignore_index=True, inplace=True)
    t2tgCount: int = df["count"].loc[12] + df["count"].loc[44]
    df = df[df[X_COL] != "text-to-text-generation"]
    df = pandas.concat(
        objs=[
            df,
            DataFrame(
                data={"tasks": ["text-to-text-generation"], "count": [t2tgCount]}
            ),
        ],
        ignore_index=True,
    )
    df.sort_values(
        by="count",
        axis=0,
        ignore_index=True,
        inplace=True,
        ascending=False,
    )

    #    print(df[X_COL].to_list())
    #    quit()

    plt.figure(figsize=(18, 9))
    for idx, value in enumerate(df[Y_COL]):
        plt.bar(
            df[X_COL][idx],
            value,
            color=list(XKCD_COLORS.values())[idx],
            label=f"{df[X_COL][idx]}",
        )
        plt.text(
            df[X_COL][idx],
            value,
            str(value),
            ha="center",
            va="bottom",
            fontsize=FONTSIZE - 4,
            rotation=30,
        )

    plt.bar(df[X_COL], df[Y_COL], color=XKCD_COLORS.values())
    plt.xlabel("PTM Task", fontsize=FONTSIZE)
    plt.ylabel("Metadata Count", fontsize=FONTSIZE)
    plt.xticks([])
    plt.yscale("log")
    # plt.legend(loc="upper left", ncol=len(df["task_name"])//5, fontsize=FONTSIZE, bbox_to_anchor=(1,1))
    plt.legend(loc="upper left", ncol=2, fontsize=FONTSIZE, bbox_to_anchor=(1, 1))
    plt.title("Captured Metadata per PTM Task")
    plt.tight_layout()
    plt.savefig("amountOfMetadataCapturedPerPTMTask.pdf")


if __name__ == "__main__":
    main()
