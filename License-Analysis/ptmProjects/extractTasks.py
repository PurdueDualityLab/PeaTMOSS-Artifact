import sqlite3
from os.path import abspath
from pathlib import Path
from sqlite3 import Connection
from typing import List

import click
import numpy
import pandas
from pandas import DataFrame

TASK_NAMES: List[str] = [
    "summarization",
    "time-series-forecasting",
    "tabular-classification",
    "voice-activity-detection",
    "none",
    "text-generation",
    "text-to-image",
    "image-segmentation",
    "image-text-retrieval",
    "document-question-answering",
    "zero-shot-image-classification",
    "audio-captioning",
    "table-question-answering",
    "automatic-speech-recognition",
    "sentence-embeddings",
    "text-to-text-generation",
    "sentence-similarity",
    "reinforcement-learning",
    "depth-estimation",
    "conversational",
    "video-classification",
    "text-to-speech",
    "audio-to-audio",
    "graph neural networksdepth-estimation",
    "text2text-generation",
    "image-classification",
    "audio-classification",
    "image-super-resolution",
    "translation",
    "object-detection",
    "unconditional-image-generation",
    "feature-extraction",
    "text-to-audio",
    "audio-generation",
    "tabular-regression",
    "visual-question-answering",
    "robotics",
    "graph-machine-learning",
    "token-classification",
    "image-text-matching",
    "information-extraction",
    "dense-passage-retrieval",
    "speaker-diarization",
    "text-classification",
    "image-to-text",
    "question-answering",
    "image-to-image",
    "text-to-video",
    "fill-mask",
    "zero-shot-classification",
]


def loadTable(table: str, con: Connection) -> DataFrame:
    query: str = "SELECT * FROM {}"
    df: DataFrame = pandas.read_sql_query(sql=query.format(table), con=con)
    return df


def mergeTables(tags: DataFrame, modelTags: DataFrame, models: DataFrame) -> DataFrame:
    tags.rename(columns={"id": "tag_id"}, inplace=True)
    models.rename(columns={"id": "model_id"}, inplace=True)

    foo: DataFrame = modelTags.merge(right=tags, how="left", on="tag_id")
    foo.drop(labels="tag_id", axis=1, inplace=True)

    bar: DataFrame = foo.merge(right=models, how="left", on="model_id")

    bar["domain"] = numpy.where(
        bar["name"] == "summarization",
        "Natural Language Processing",
        numpy.where(
            bar["name"] == "time-series-forecasting",
            "Other",
            numpy.where(
                bar["name"] == "tabular-classification",
                "Tabular",
                numpy.where(
                    bar["name"] == "voice-activity-detection",
                    "Audio",
                    numpy.where(
                        bar["name"] == "none",
                        "Other",
                        numpy.where(
                            bar["name"] == "text-generation",
                            "Natural Language Processing",
                            numpy.where(
                                bar["name"] == "text-to-image",
                                "Multimodal",
                                numpy.where(
                                    bar["name"] == "image-segmentation",
                                    "Computer Vision",
                                    numpy.where(
                                        bar["name"] == "image-text-retrieval",
                                        "Other",
                                        numpy.where(
                                            bar["name"]
                                            == "document-question-answering",
                                            "Multimodal",
                                            numpy.where(
                                                bar["name"]
                                                == "zero-shot-image-classification",
                                                "Computer Vision",
                                                numpy.where(
                                                    bar["name"] == "audio-captioning",
                                                    "Other",
                                                    numpy.where(
                                                        bar["name"]
                                                        == "table-question-answering",
                                                        "Other",
                                                        numpy.where(
                                                            bar["name"]
                                                            == "automatic-speech-recognition",
                                                            "Audio",
                                                            numpy.where(
                                                                bar["name"]
                                                                == "sentence-embeddings",
                                                                "Other",
                                                                numpy.where(
                                                                    bar["name"]
                                                                    == "text-to-text-generation",
                                                                    "Natural Language Processing",
                                                                    numpy.where(
                                                                        bar["name"]
                                                                        == "sentence-similarity",
                                                                        "Natural Language Processing",
                                                                        numpy.where(
                                                                            bar["name"]
                                                                            == "reinforcement-learning",
                                                                            "Reinforcement Learning",
                                                                            numpy.where(
                                                                                bar[
                                                                                    "name"
                                                                                ]
                                                                                == "depth-estimation",
                                                                                "Computer Vision",
                                                                                numpy.where(
                                                                                    bar[
                                                                                        "name"
                                                                                    ]
                                                                                    == "conversational",
                                                                                    "Natural Language Processing",
                                                                                    numpy.where(
                                                                                        bar[
                                                                                            "name"
                                                                                        ]
                                                                                        == "video-classification",
                                                                                        "Computer Vision",
                                                                                        numpy.where(
                                                                                            bar[
                                                                                                "name"
                                                                                            ]
                                                                                            == "text-to-speech",
                                                                                            "Audio",
                                                                                            numpy.where(
                                                                                                bar[
                                                                                                    "name"
                                                                                                ]
                                                                                                == "audio-to-audio",
                                                                                                "Audio",
                                                                                                numpy.where(
                                                                                                    bar[
                                                                                                        "name"
                                                                                                    ]
                                                                                                    == "graph neural networksdepth-estimation",
                                                                                                    "Multimodal",
                                                                                                    numpy.where(
                                                                                                        bar[
                                                                                                            "name"
                                                                                                        ]
                                                                                                        == "text2text-generation",
                                                                                                        "Natural Language Processing",
                                                                                                        numpy.where(
                                                                                                            bar[
                                                                                                                "name"
                                                                                                            ]
                                                                                                            == "image-classification",
                                                                                                            "Computer Vision",
                                                                                                            numpy.where(
                                                                                                                bar[
                                                                                                                    "name"
                                                                                                                ]
                                                                                                                == "audio-classification",
                                                                                                                "Audio",
                                                                                                                numpy.where(
                                                                                                                    bar[
                                                                                                                        "name"
                                                                                                                    ]
                                                                                                                    == "image-super-resolution",
                                                                                                                    "Other",
                                                                                                                    numpy.where(
                                                                                                                        bar[
                                                                                                                            "name"
                                                                                                                        ]
                                                                                                                        == "translation",
                                                                                                                        "Natural Language Processing",
                                                                                                                        numpy.where(
                                                                                                                            bar[
                                                                                                                                "name"
                                                                                                                            ]
                                                                                                                            == "object-detection",
                                                                                                                            "Computer Vision",
                                                                                                                            numpy.where(
                                                                                                                                bar[
                                                                                                                                    "name"
                                                                                                                                ]
                                                                                                                                == "unconditional-image-generation",
                                                                                                                                "Computer Vision",
                                                                                                                                numpy.where(
                                                                                                                                    bar[
                                                                                                                                        "name"
                                                                                                                                    ]
                                                                                                                                    == "feature-extraction",
                                                                                                                                    "Multimodal",
                                                                                                                                    numpy.where(
                                                                                                                                        bar[
                                                                                                                                            "name"
                                                                                                                                        ]
                                                                                                                                        == "text-to-audio",
                                                                                                                                        "Audio",
                                                                                                                                        numpy.where(
                                                                                                                                            bar[
                                                                                                                                                "name"
                                                                                                                                            ]
                                                                                                                                            == "audio-generation",
                                                                                                                                            "Other",
                                                                                                                                            numpy.where(
                                                                                                                                                bar[
                                                                                                                                                    "name"
                                                                                                                                                ]
                                                                                                                                                == "tabular-regression",
                                                                                                                                                "Tabular",
                                                                                                                                                numpy.where(
                                                                                                                                                    bar[
                                                                                                                                                        "name"
                                                                                                                                                    ]
                                                                                                                                                    == "visual-question-answering",
                                                                                                                                                    "Multimodal",
                                                                                                                                                    numpy.where(
                                                                                                                                                        bar[
                                                                                                                                                            "name"
                                                                                                                                                        ]
                                                                                                                                                        == "robotics",
                                                                                                                                                        "Reinforcement Learning",
                                                                                                                                                        numpy.where(
                                                                                                                                                            bar[
                                                                                                                                                                "name"
                                                                                                                                                            ]
                                                                                                                                                            == "graph-machine-learning",
                                                                                                                                                            "Multimodal",
                                                                                                                                                            numpy.where(
                                                                                                                                                                bar[
                                                                                                                                                                    "name"
                                                                                                                                                                ]
                                                                                                                                                                == "token-classification",
                                                                                                                                                                "Natural Language Processing",
                                                                                                                                                                numpy.where(
                                                                                                                                                                    bar[
                                                                                                                                                                        "name"
                                                                                                                                                                    ]
                                                                                                                                                                    == "image-text-matching",
                                                                                                                                                                    "Other",
                                                                                                                                                                    numpy.where(
                                                                                                                                                                        bar[
                                                                                                                                                                            "name"
                                                                                                                                                                        ]
                                                                                                                                                                        == "information-extraction",
                                                                                                                                                                        "Other",
                                                                                                                                                                        numpy.where(
                                                                                                                                                                            bar[
                                                                                                                                                                                "name"
                                                                                                                                                                            ]
                                                                                                                                                                            == "dense-passage-retrieval",
                                                                                                                                                                            "Other",
                                                                                                                                                                            numpy.where(
                                                                                                                                                                                bar[
                                                                                                                                                                                    "name"
                                                                                                                                                                                ]
                                                                                                                                                                                == "speaker-diarization",
                                                                                                                                                                                "Other",
                                                                                                                                                                                numpy.where(
                                                                                                                                                                                    bar[
                                                                                                                                                                                        "name"
                                                                                                                                                                                    ]
                                                                                                                                                                                    == "text-classification",
                                                                                                                                                                                    "Natural Language Processing",
                                                                                                                                                                                    numpy.where(
                                                                                                                                                                                        bar[
                                                                                                                                                                                            "name"
                                                                                                                                                                                        ]
                                                                                                                                                                                        == "image-to-text",
                                                                                                                                                                                        "Multimodal",
                                                                                                                                                                                        numpy.where(
                                                                                                                                                                                            bar[
                                                                                                                                                                                                "name"
                                                                                                                                                                                            ]
                                                                                                                                                                                            == "question-answering",
                                                                                                                                                                                            "Natural Language Processing",
                                                                                                                                                                                            numpy.where(
                                                                                                                                                                                                bar[
                                                                                                                                                                                                    "name"
                                                                                                                                                                                                ]
                                                                                                                                                                                                == "image-to-image",
                                                                                                                                                                                                "Computer Vision",
                                                                                                                                                                                                numpy.where(
                                                                                                                                                                                                    bar[
                                                                                                                                                                                                        "name"
                                                                                                                                                                                                    ]
                                                                                                                                                                                                    == "text-to-video",
                                                                                                                                                                                                    "Other",
                                                                                                                                                                                                    numpy.where(
                                                                                                                                                                                                        bar[
                                                                                                                                                                                                            "name"
                                                                                                                                                                                                        ]
                                                                                                                                                                                                        == "fill-mask",
                                                                                                                                                                                                        "Natural Language Processing",
                                                                                                                                                                                                        numpy.where(
                                                                                                                                                                                                            bar[
                                                                                                                                                                                                                "name"
                                                                                                                                                                                                            ]
                                                                                                                                                                                                            == "zero-shot-classification",
                                                                                                                                                                                                            "Other",
                                                                                                                                                                                                            "None",
                                                                                                                                                                                                        ),
                                                                                                                                                                                                    ),
                                                                                                                                                                                                ),
                                                                                                                                                                                            ),
                                                                                                                                                                                        ),
                                                                                                                                                                                    ),
                                                                                                                                                                                ),
                                                                                                                                                                            ),
                                                                                                                                                                        ),
                                                                                                                                                                    ),
                                                                                                                                                                ),
                                                                                                                                                            ),
                                                                                                                                                        ),
                                                                                                                                                    ),
                                                                                                                                                ),
                                                                                                                                            ),
                                                                                                                                        ),
                                                                                                                                    ),
                                                                                                                                ),
                                                                                                                            ),
                                                                                                                        ),
                                                                                                                    ),
                                                                                                                ),
                                                                                                            ),
                                                                                                        ),
                                                                                                    ),
                                                                                                ),
                                                                                            ),
                                                                                        ),
                                                                                    ),
                                                                                ),
                                                                            ),
                                                                        ),
                                                                    ),
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    bar.rename(columns={"name": "task_name"}, inplace=True)

    return bar


def postProcess(df: DataFrame) -> DataFrame:
    badColumns: List[str] = [
        "model_hub_id",
        "sha",
        "downloads",
        "likes",
        "has_snapshot",
        "ptm_issues_id",
        "ptm_pull_requests_id",
    ]

    df.drop(labels=badColumns, axis=1, inplace=True)

    foo: DataFrame = df[df["task_name"].isin(TASK_NAMES)].reset_index(drop=True)

    return foo


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
    default="../../data/tasks/ptmProjectTasks.json",
    type=Path,
    help="Path to store application output",
    show_default=True,
)
def main(db: Path, output: Path) -> None:
    dbFilepath: Path = Path(abspath(db))
    outputFilepath: Path = Path(abspath(output))

    print(f"Reading data from {dbFilepath}...")
    con: Connection = sqlite3.connect(database=dbFilepath)

    tags: DataFrame = loadTable(table="tag", con=con)
    modelTags: DataFrame = loadTable(table="model_to_tag", con=con)
    models: DataFrame = loadTable(table="model", con=con)

    con.close()

    df: DataFrame = mergeTables(tags=tags, modelTags=modelTags, models=models)

    print(f"Writing data to {outputFilepath}...")
    postProcess(df=df).T.to_json(path_or_buf=output, indent=4)


if __name__ == "__main__":
    main()
