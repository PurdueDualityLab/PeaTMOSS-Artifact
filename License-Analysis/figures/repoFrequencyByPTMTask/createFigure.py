import matplotlib.pyplot as plt
import pandas
from matplotlib.colors import XKCD_COLORS
from pandas import DataFrame

FONTSIZE: int = 12


def main() -> None:
    df: DataFrame = pandas.read_json(
        path_or_buf="../../data/ghProjectsPerPTMTask.json"
    ).T.sort_values(by="project_count", ascending=False, ignore_index=True)

    plt.figure(figsize=(18, 9))
    for idx, value in enumerate(df["project_count"]):
        plt.bar(
            df["task_name"][idx],
            value,
            color=list(XKCD_COLORS.values())[idx],
            label=f'{df["task_name"][idx]}',
        )
        plt.text(
            df["task_name"][idx],
            value,
            str(value),
            ha="center",
            va="bottom",
            fontsize=FONTSIZE - 4,
        )

    plt.bar(df["task_name"], df["project_count"], color=XKCD_COLORS.values())
    plt.xlabel("PTM Task", fontsize=FONTSIZE)
    plt.ylabel("Application Count", fontsize=FONTSIZE)
    plt.xticks([])
    plt.yscale("log")
    # plt.legend(loc="upper left", ncol=len(df["task_name"])//5, fontsize=FONTSIZE, bbox_to_anchor=(1,1))
    plt.legend(loc="upper left", ncol=2, fontsize=FONTSIZE, bbox_to_anchor=(1, 1))
    plt.title("Frequency of Applications per PTM Task")
    plt.tight_layout()
    plt.savefig("frequencyOfApplicationsPerPTMTask.pdf")


if __name__ == "__main__":
    main()
