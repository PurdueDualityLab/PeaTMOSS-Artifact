# MSR 2024 Code

## Table of Contents

- [MSR 2024 Code](#msr-2024-code)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [How to Run](#how-to-run)
    - [Setup Development Enviornment](#setup-development-enviornment)
      - [Optional: Setup `pre-commit`](#optional-setup-pre-commit)
    - [Execute Scripts](#execute-scripts)
  - [Required Data](#required-data)
    - [Replace `data` Placeholder Files](#replace-data-placeholder-files)

## About

This repository contains the source code that we created in assistance for our
submission to MSR 2024.

______________________________________________________________________

## How to Run

### Setup Development Enviornment

1. Create `python3.10` virtual environment: `python3.10 -m venv env`
1. Sourc virtual environment: `source env/bin/activate`
1. Install `requirements.txt`: `pip install -r requirments.txt`
1. Install `poetry` dependencies: `poetry install`

#### Optional: Setup `pre-commit`

This project uses `pre-commit` to enforce similar code styles and
file-permission checks.

1. Install `pre-commit`:
   [`pre-commit` install instructions](https://pre-commit.com/#install)
1. Initialize `pre-commit` within the project: `pre-commit install`
1. Update hooks: `pre-commit autoupdate`

### Execute Scripts

For python scripts that do not generate figures, follow this execution pattern:

**NOTE**: For this tutorial we are using the `/ptmProjects` directory
and its contained scripts. Please adjust this to fit your specific example.

1. Change directory to the script's directory: `cd /ptmProjects`
1. See script options: `python extractLicenses.py --help`
1. Run script with defaults: `python extractLicenses.py`

______________________________________________________________________

## Required Data

You will need to have access to the *PeaTMOSS* dataset.

You can find out more information about how to access this dataset at [Globus Share](https://transfer.rcac.purdue.edu/file-manager?origin_id=ff978999-16c2-4b50-ac7a-947ffdc3eb1d&origin_path=%2F).

### Replace `data` Placeholder Files

Within the `data` folder exists file with the following pattern:

- `FILENAME.EXTENSION.gitkeep`

These are *empty* files that can be left alone or deleted with no consequences.
However, the relevant file (i.e `PeaTMOSS.db`) needs to be copied from the
*PeaTMOSS* dataset into the same directory of the files with the above pattern
for **scripts to operate with their default commandline values**. If you are not
using the script defaults, you can ignore this section.
