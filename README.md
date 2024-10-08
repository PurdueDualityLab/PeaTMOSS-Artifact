# MSR 2024 Artifact

## About

> This repository contains the source code and dataset examples for our MSR'24 paper `PeaTMOSS: A Dataset and Initial Analysis of Pre-Trained Models in Open-Source Software`.

## Repository Structure

- **PeaTMOSS Dataset** ($4, 6)
  - `README.md`
  - `PeaTMOSS.sql`
  - `Examples/`

- **LLM-Pipeline/** ($5)
  - `README.md`
  - `Accurate_pipeline`
  - `Cheap_pipeline`

- **License-Analysis/** ($7)
  - `README.md`
  - `analyzeIncompatibilities/`
  - `data/`
  - `figures/`
  - `ghRepos`
  - `projectPairings/`
  - `ptmProjects/`

  

## PeaTMOSS Dataset
- [PeaTMOSS Demos](#peatmoss-demos)
  - [About](#about)
  - [Metadata Description](#metadata-description)
  - [Dependencies](#dependencies)
  - [How To Install](#how-to-install)
  - [How to Run](#how-to-run)
  - [Tutorial](#tutorial)
    - [Using SQL to query the database](#using-sql-to-query-the-database)
    - [Research Question Example (SQL)](#research-question-example-sql)
    - [Using ORMs to query the database](#using-orms-to-query-the-database)
    - [Research Question Example (ORM)](#research-question-example-orm)

## About

This repository contains a [zipped sample](PeaTMOSS_Sample.db.zip) of the *PeaTMOSS* dataset,
as well as a script that demonstrates possible interactions with the SQLite database used to store the metadata dataset.
The complete *PeaTMOSS* dataset contains snapshots of **P**re-**T**rained machine learning **M**odel (PTM) repositories and the downstream Open-Source GitHub repositories that reuse the PTMs,
metadata about the PTMs,
the pull requests and issues of the GitHub Repositories,
and links between the downstream GitHub repositories and the PTM models.
The schema of the SQLite database is specified by [PeaTMOSS.py](PeaTMOSS.py) and [PeatMOSS.sql](PeatMOSS.sql).
The sample of the database is [PeaTMOSS_sample.db](PeaTMOSS_sample.db).
The full database, as well as all captured repository snapshots are available [here](https://transfer.rcac.purdue.edu/file-manager?origin_id=ff978999-16c2-4b50-ac7a-947ffdc3eb1d&origin_path=%2F)
#### - Note: When unzipping .tar.gz snapshots, include the flag
```bash
--strip-components=4
```
in the tar statement, like so
```bash
tar --strip-components=4 -xvzf {name}.tar.gz
```
If you do not do this, you will have 4 extraneous parent directories that encase the repository.


The script that we used to generate figures in $6 is available in [script_plot.py](/Plots/script_plot.py)

## Globus

### Globus Share
All zipped repos and the full metadata dataset are available through [Globus Share](https://transfer.rcac.purdue.edu/file-manager?origin_id=ff978999-16c2-4b50-ac7a-947ffdc3eb1d&origin_path=%2F)

If you do not have an account, follow the Globus docs on [how to sign up](https://docs.globus.org/how-to/get-started/). You may create an account through a partnered organization if you are a part of that organization, or through Google or ORCID accounts.

### Globus Connect Personal
To access the metadata dataset using the `globus.py` script provided in the repository:
1. [Download Globus Connect Personal](https://www.globus.org/globus-connect-personal)
1. Create your own private Globus collection on
[Mac](https://docs.globus.org/how-to/globus-connect-personal-mac/),
[Windows](https://docs.globus.org/how-to/globus-connect-personal-windows/.), or
[Linux](https://docs.globus.org/how-to/globus-connect-personal-linux/)
1. Once this is created, make sure your Globus Personal Connect is running before executing `globus.py`

**NOTE:** In some cases, you may run into permission issues on Globus when running the script.
If this is the case, you will need to change `local_endpoint.endpoint_id`, located on [line 29](globus.py#29), to your private collection's UUID:
```python
local_endpoint_id = local_endpoint.endpoint_id
``` 

To locate your private collecion's UUID, click on the Globus icon on your taskbar and select "Web: Collection Details".
On this page, scroll down to the bottom where the UUID field for your collection should be visible, and replace the variable with your collection's UUID expressed as a string.
Then, use the activities tab to terminate the existing transfer and rerun globus.py.

 

## Metadata Description
The following model hubs are captured in our database:

- [Hugging Face](https://huggingface.co/)
- [PyTorch Hub](https://pytorch.org/hub/)

The content for each specific model hub is listed in the table below:

|   Model hub  |  #PTMs  | #Snapshotted Repos | #Discussions (PRs, issues) | #Links | Size of Zipped Snapshots |
|:------------:|:-------:|:------------------:|:--------------------------:|:------:|:------------------------:|
| Hugging Face | 281,638 |       14,296       |           59,011           | 30,514 |           44TB           |
|  PyTorch Hub |   362   |         361        |           52,161           | 13,823 |           1.3GB          |

We also offer two different formats of our datasets. An overview of these two formats can be found in the table below:
|  Formats |                                                                    Description                                                                   |  Size  |
|:--------:|:------------------------------------------------------------------------------------------------------------------------------------------------:|:------:|
| Metadata |                          It contains only the metadata of the PTM packagesr and a subset of the GitHub project metadata.                         |  8.32GB (7.12GB + 1.20 GB enhanced metadata) |
|   Full   | It contains all metadata, adding the PTM package contents in each published version, and git history of the main branhes of the GitHub projects. | 48.2TB |

## Dependencies

The scripts in the project depend upon the following software:

- [`Python 3.11`](https://www.python.org/downloads/release/python-3110/)
- [`SQLAlchemy 2.0`](https://www.sqlalchemy.org)

> Package dependencies are given in [`environment.yml`](environment.yml) and
> handled by [`anaconda`](https://anaconda.org/)

## How To Install

To run the scripts in this project, you must install python 3.11 and SQLAlchemy v2.0 or greater.

These package can be installed using the `anaconda` environment manager
1. Install the latest version of anaconda from [here](https://www.anaconda.com/download)
1. run `conda env create -f environment.yml` to create the anaconda environment `PeaTMOSS`
1. Activate the environment using `conda activate PeaTMOSS`

Alternatively, you can navigate to each packages respective pages and install them.

## How to Run

After [installing the anaconda environment](#how-to-install), each demo script can be run using `python3 script_name.py`

## Tutorial
This section will explain how to use SQL and SQLAlchemy to interact with the database to answer the research questions outlined in some of the future work we propose. 

### Using SQL to query the database
One option users have to interact with the metadata dataset is to use plain SQL. The metadata dataset is stored in a SQLite database file called PeaTMOSS.db, which can be found in the [Anonymous Link]. This file can be queried through standard SQL queries, and this can be done from a terminal using sqlite3: https://sqlite.org/cli.html. Single queries can be executed like
```bash
$ sqlite3 PeaTMOSS.db '{query statement}'
```
Alternatively, you can start an SQLite instance by simply executing
```bash
$ sqlite3 PeaTMOSS.db
```
which can be terminated by `CTRL + D` or `.quit`. To output queries to files, the .output command can be used
```bash
sqlite> .output {filename}.txt
```

### Research Question Example (SQL)

The following example has to do with research question GH2: "What do developers on GitHub discuss related to PTM use, e.g., in issues, and pull requests? What are developers’ sentiments regarding PTM use? Do the people do pull requests of PTMs have the right expertise?" 

If someone wants to observe what developers on GitHub are currently discussing related to PTM usage, they can look at discussions in GitHub issues and pull requests. The following SQLite example shows queries that would help accomplish this task.

1. First, we will create an sqlite3 instance:
```bash
$ sqlite3 PeaTMOSS.db
```

3. Then, we will create an output file for our issues query, then execute that query:
```bash
sqlite> .output issues.txt
sqlite> SELECT id, title FROM github_issue WHERE state = 'OPEN' ORDER BY updated_at DESC LIMIT 100;
```
Output:

<img width="614" alt="6c66d24cac7cf9542f91d4a875bb1abe" src="https://github.com/PurdueDualityLab/PeaTMOSS-Demos/assets/70859381/3f6d9508-76de-4386-808b-0d9157a8392b">

The above query selects the ID and Title fields from the github_issue table, and chooses the 100 most recent issues that are still open.

3. Next, we will create an output file for our pull requests query, then execute that query:
```bash
sqlite> .output pull_requests.txt
sqlite> SELECT id, title FROM github_pull_request WHERE state = 'OPEN' OR state = 'MERGED' ORDER BY updated_at DESC LIMIT 100;
```
Output:

<img width="611" alt="b128657ee024e2441110090f3bc19ea6" src="https://github.com/PurdueDualityLab/PeaTMOSS-Demos/assets/70859381/b3773972-9dd0-43e6-8244-3ab1ac94d4dc">

Notice that the query is very similar to the issues query, as we are looking for similar information. The above query selects the ID and Title fields from the github_pull_request table, and chooses the 100 most recent pull requests that are either open or merged.

Querying this data can assist when beginning to observe current/recent discussions in GitHub about PTMs. From here, you may adjust these queries to include more/less entries by changing the LIMIT value, or you may adjust which fields the queries return. For example, if you want more detailed information you could select the "body" field in either table.


### Using ORMs to query the database

This section will include more details about the demo provided in the repository, PeaTMOSS_demo.py. Once again, this method requires the PeaTMOSS.db file, which can be found in the [Globus Share](https://transfer.rcac.purdue.edu/file-manager?origin_id=ff978999-16c2-4b50-ac7a-947ffdc3eb1d&origin_path=%2F). Prior to running this demo, ensure that the conda environment has been created and activated, or you may run into errors. 

The purpose of the demo, as described at by the comment at the top of its file, is to demonstrate how one may use SQLAlchemy to address one of the research questions. The question being addressed in the demo is I1: "It can be difficult to interpret model popularity numbers by download rates. To what extent does a PTM’s download rates correlate with the number of GitHub projects that rely on it, or the popularity of the GitHub projects?". The demo accomplishes this by looking at two main fields: the number of times a model is downloaded from its model hub, and the number of times a model is reused in a GitHub repository. The demo finds the 100 most downloaded models, and finds how many times each of those models are reused. Users can take this information and attempt to find a correlation.

### Research Question Example (ORM)
[`PeaTMOSS_demo.py`](examples/PeaTMOSS_demo.py) utilizes [`PeaTMOSS.py`](PeaTMOSS.py), which is used to describe the structure of the database so that we may interact with it using SQLAlchemy. To begin, you must create and SQLAlchemy engine using the database file
```python
import sqlalchemy
engine = sqlalchemy.create_engine(f"sqlite:///{path}")
```
where `path` is a string that describes the filepath to the database file.
Both relative and absolute file paths can be used.

To find the 100 most downloaded models, we will query the model table

```python
import sqlalchemy
from sqlalchemy.orm import Session
from PeaTMOSS import *

query_name_downloads = sqlalchemy.select(Model.id, Model.context_id, Model.downloads).limit(100).order_by(sqlalchemy.desc(Model.downloads))
```

and execute the query

```python
models = session.execute(query_name_downloads).all()
```

For each of these models, we want to know how many times they are being reused. The model_to_reuse_repository contains fields for model IDs and reuse repository IDs, effectively linking them together. If a model is reused in multiple repository its ID will show up multiple times in the model_to_reuse_repository table. Therefore, we want to see if these highly downloaded models are also highly reused. We can do this querying the model_to_reuse_repository table and only select entries where the model_id field is equivalent to the current model's ID:

```python
for model in models:
    #...
    query_num_reuses = sqlalchemy.select(PeaTMOSS.model_to_reuse_repository.columns.model_id)\
                                  .where(PeaTMOSS.model_to_reuse_repository.columns.model_id == model.id)

```
This query will select all the instances of the current model's ID appears in the model_to_reuse_repository table. If we execute this query and count the number of elements in the result, we have the number of times that model has been reused:
```python
num_reuses = len(session.execute(query_num_reuses).all())
```

In each iteration of the loop we can store this information in dictionaries, where the keys can be the names of the models:
```python
for model in models:
    highly_downloaded[model.context_id] = model.downloads
    #...
    #...
    reused_rates[model.context_id] = num_reuses
```
And then at the end, we can simply print the results. From there, users may observe a level of correlation using a method they see fit. 

Download Results:

<img width="649" alt="5349fd8861432ed693ca27429f569eb3" src="https://github.com/PurdueDualityLab/PeaTMOSS-Demos/assets/70859381/f5d6ee38-adf1-4978-9ae4-6eedb4f5e9be">

Reuse Results:

<img width="656" alt="003113aa18d146f9babc7e9ae1c6c3e0" src="https://github.com/PurdueDualityLab/PeaTMOSS-Demos/assets/70859381/6b835260-8afa-4f1b-9104-9d6a54c9ed44">


## Citing PeaTMOSS
```latex
@inproceedings{PeaTMOSS,
  title={PeaTMOSS: A Dataset and Initial Analysis of Pre-Trained Models in Open-Source Software},
  author={Wenxin Jiang, Jerin Yasmin, Jason Jones, Nicholas Synovic, Jiashen Kuo, Yuan Tian, George K. Thiruvathukal, and James C. Davis},
  booktitle={Proceedings of the 21th Annual Conference on Mining
Software Repositories (MSR'24)},
  year={2024}
}
```
