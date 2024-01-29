import subprocess
from pathlib import PurePath
from subprocess import CompletedProcess
from typing import List
from urllib.parse import ParseResult, urlparse

# TODO: Merge cloneBareRepo() and cloneRepo() as they use the same code with
# exception of the gitCommand variable and a renamed argument


def cloneBareRepo(url: str, gitCloneBarePath: PurePath) -> CompletedProcess | bool:
    author: str
    repo: str

    gitCommand: List[str] = ["git", "clone", "--bare", "-q"]

    try:
        parsedURL: ParseResult = urlparse(url)
        pathSplit: List[str] = parsedURL.path.strip("/").split("/")
    except TypeError:
        return False

    if len(pathSplit) == 1:
        author = parsedURL.netloc.strip()
        repo = pathSplit[0]
    else:
        author = pathSplit[0]
        repo = pathSplit[1]

    gitPath: PurePath = PurePath(f"{gitCloneBarePath}/{author}/{repo}")
    gitCommand.extend([url, gitPath])

    return subprocess.run(args=gitCommand)


def cloneRepo(url: str, rootGitClonePath: PurePath) -> CompletedProcess:
    author: str
    repo: str

    gitCommand: List[str] = ["git", "clone", "-q"]

    try:
        parsedURL: ParseResult = urlparse(url)
        pathSplit: List[str] = parsedURL.path.strip("/").split("/")
    except TypeError:
        print(f"Error Cloning Repo {url}")
        return False

    if len(pathSplit) == 1:
        author = parsedURL.netloc.strip()
        repo = pathSplit[0]
    else:
        author = pathSplit[0]
        repo = pathSplit[1]

    gitPath: PurePath = PurePath(f"{rootGitClonePath}/{author}/{repo}")
    gitCommand.extend([url, gitPath])

    return subprocess.run(args=gitCommand, shell=False, stderr=subprocess.DEVNULL)


def getLatestGitCommitOfFile(gitProjectPath: PurePath, filepath: PurePath) -> str:
    gitCommand: List[str] = [
        "git",
        "--no-pager",
        "-C",
        gitProjectPath,
        "log",
        "-n 1",
        '--format="%H"',
        "--",
        filepath,
    ]

    process: CompletedProcess = subprocess.run(
        args=gitCommand, shell=False, stdout=subprocess.PIPE
    )

    return process.stdout.decode(encoding="UTF-8").strip().replace('"', "")


def getLatestGitCommit(gitProjectPath: PurePath) -> str:
    gitCommand: List[str] = [
        "git",
        "--no-pager",
        "-C",
        gitProjectPath,
        "log",
        "-n 1",
        '--format="%H"',
    ]

    process: CompletedProcess = subprocess.run(
        args=gitCommand, shell=False, stdout=subprocess.PIPE
    )

    return process.stdout.decode(encoding="UTF-8").strip().replace('"', "")
