import matplotlib.pyplot as plt
import pandas
from matplotlib.colors import XKCD_COLORS
from pandas import DataFrame

FONTSIZE: int = 12


def main() -> None:
    df: DataFrame = pandas.read_json(
        path_or_buf="../../data/ghProjectsPerPTMTask.json"
    ).T.sort_values(by="project_count", ascending=False, ignore_index=True)

    pivot: DataFrame = df.pivot(
        index="domain", columns="task_name", values="project_count"
    )

    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values(by="Total", ascending=False)
    del pivot["Total"]

    pivot.plot(kind="bar", figsize=(20, 6))

    plt.title("Frequency of Applications per PTM Task")
    plt.xlabel("PTM Task", fontsize=FONTSIZE)
    plt.ylabel("Application Count", fontsize=FONTSIZE)
    plt.yscale("log")
    plt.xticks(rotation=0)
    plt.legend(title="Category")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), ncols=2)

    for p in plt.gca().patches:
        plt.gca().annotate(
            str(p.get_height()),
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            xytext=(0, 10),
            textcoords="offset points",
        )

    plt.tight_layout()

    plt.savefig("frequencyOfApplicationsPerPTMTask_test.pdf")


if __name__ == "__main__":
    main()
