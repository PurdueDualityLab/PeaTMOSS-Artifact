from sqlalchemy.inspection import inspect
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship, Session
from sqlalchemy import inspect, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.schema import DropTable
from sqlalchemy import desc, func
from PeaTMOSS import *
from ast import literal_eval
from tqdm import tqdm
import pathlib
import json
import os

import sys
import csv
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


# This function queries the given table to see if the given value is already in the table
# If it is, it returns the object in the table
# If it is not, it adds the value to the table and returns the object in the table
def upsert(session: Session, table_class: BASE, data: String) -> BASE:
    obj = session.query(table_class).filter(table_class.name == data).first()
    if not obj:
        obj = table_class(name=data)
        session.add(obj)
    return obj

def upsert_gh_user(session: Session, data: dict) -> GitHubUser:
    obj = session.query(GitHubUser).filter(GitHubUser.login == data.get("login")).first()
    if not obj:
        obj = GitHubUser(login=data.get("login"),
                         email=data.get("email"))
        session.add(obj)
    return obj


def insert_hf_models(engine):
    file_path = "json/models/HF_model_discussions_commits_formatted_dedup.json"
    with Session(engine) as session:
        with open(file_path, "r") as json_file:
            dicts = json.load(json_file)
            length = len(list(dicts))
            print(f"Here are the dict keys: {dicts[0].keys()}")
        with open(file_path, "r") as json_file:
            dicts = json.load(json_file)
            for row in tqdm(dicts, total=length):
                try:
                    # print(f"Discussions keys: {literal_eval(row['discussions'])}") if row["discussions"] else None
                    session.add(Model(context_id=row["context_id"],
                                    model_hub_id=1,
                                    repo_url=row["repo_url"],
                                    sha=row["sha"],
                                    downloads=row["downloads"],
                                    likes=row["likes"],
                                    architectures=[upsert(session, Architecture, architecture)for architecture in row.get("architectures", [])] if row.get("architectures", []) else [],
                                    authors=[upsert(session, Author, author) for author in row.get("authors", [])] if row.get("authors", []) else [],
                                    datasets=[upsert(session, Dataset, dataset) for dataset in row.get("datasets", [])] if row.get("datasets", []) else [],
                                    discussions=[Discussion(title=discussion["title"],
                                                            status=discussion["status"],
                                                            num=discussion["num"],
                                                            repo_id=discussion["repo_id"],
                                                            repo_type=discussion["repo_type"],
                                                            author=[upsert(session, Author, discussion["author"])],
                                                            is_pull_request=discussion["is_pull_request"],
                                                            created_at=discussion["created_at"],
                                                            endpoint=discussion["endpoint"],
                                                            conflicting_files=[FilePath(path=path) for path in discussion.get("conflicting_files", [])] if discussion.get("conflicting_files", []) and not isinstance(discussion.get("conflicting_files", []), bool) else [],
                                                            target_branch=discussion["target_branch"],
                                                            merge_commit_oid=discussion["merge_commit_oid"],
                                                            events=[DiscussionEvent(event_id=event["id"],
                                                                                    type=event["type"],
                                                                                    created_at=event["created_at"],
                                                                                    author=event["author"],
                                                                                    content=event.get("content"),
                                                                                    edited=event.get("edited"),
                                                                                    hidden=event.get("hidden"),
                                                                                    new_status=event.get("new_status"),
                                                                                    summary=event.get("summary"),
                                                                                    oid=event.get("oid"),
                                                                                    old_title=event.get("old_title"),
                                                                                    new_title=event.get("new_title")
                                                                                    ) for event in (discussion["events"] or []) if not None],
                                                            diff=discussion["diff"]
                                                            ) for discussion in row.get("discussions", [])] if 'Client Error' not in row.get("discussions", []) else [],
                                    hf_commits=[HFCommit(commit_id=commit["commit_id"],
                                                            authors=[upsert(session, Author, author) for author in set(commit["authors"])],
                                                            created_at=commit["created_at"],
                                                            title=commit["title"],
                                                            message=commit["message"]
                                                            ) for commit in row.get("commits", [])] if row.get("commits", []) else [],
                                    hf_gitrefs=[HFGitRef(branches=[HFGitRefInfo(name=branch["name"],
                                                                               ref=branch["ref"],
                                                                               target_commit=branch["target_commit"]
                                                                                ) for branch in ref.get("branches", [])],
                                                        tags=[HFGitRefInfo(name=tag["name"],
                                                                          ref=tag["ref"],
                                                                          target_commit=tag["target_commit"]
                                                                          ) for tag in ref.get("tags", [])]
                                                        ) for ref in row.get("git_refs", [])] if row.get("git_refs", []) else [],
                                    has_snapshot=True if row["commits"] else False,
                                    frameworks=[upsert(session, Framework, framework) for framework in row.get("framework", [])] if row.get("framework", []) else [],
                                    languages=[upsert(session, Language, language) for language in row.get("language", [])] if row.get("language", []) else [],
                                    libraries=[upsert(session, Library, library) for library in row.get("library", [])] if row.get("library", []) else [],
                                    licenses=[upsert(session, License, license) for license in row.get("license", [])] if row.get("license", []) else [],
                                    papers=[upsert(session, Paper, paper) for paper in row.get("paper", [])] if row.get("paper", []) else [],
                                    tags=[upsert(session, Tag, tag) for tag in row.get("tags", [])] if row.get("tags", []) else [],
                                    ))
                except Exception as e:
                    print(row["context_id"])
                    raise e
            session.commit()

# This uses the files in json/reuse_ to populate the database
# It assumes that all the files in the directory are json files
# It assumes that the files are in the format of the GitHub API
# It assumes that the tables have already been created
def insert_github_issues(engine):
    files = [file for file in pathlib.Path("json/reuse").rglob("*issues.json")]
    with Session(engine) as session:
        for file in tqdm(files):
            insert_github_issue(session, file)

def insert_github_issue(session: Session, file: pathlib.Path) -> list[GitHubIssue]:
    issues_list = []
    with open(file, "r") as json_file:
        issues = json.load(json_file)
        try:
            for issue in issues:
                github_issue = (GitHubIssue(
                    assignee=[upsert_gh_user(session, assignee) for assignee in issue["assignees"]],
                    author=upsert_gh_user(session, issue["author"]),
                    body=issue["body"],
                    closed=issue["closed"],
                    closed_at=issue["closedAt"],
                    comments=[GitHubComment(author=upsert_gh_user(session, comment["author"]),
                                            author_association=comment["authorAssociation"],
                                            body=comment["body"],
                                            created_at=comment["createdAt"],
                                            includes_created_edit=comment["includesCreatedEdit"],
                                            is_minimized=comment["isMinimized"],
                                            minimized_reason=comment["minimizedReason"],
                                            reaction_groups=[GitHubReactionGroup(content=reaction["content"],
                                                        total_count=reaction["users"]["totalCount"]) for reaction in comment["reactionGroups"]]) for comment in issue["comments"]],
                    created_at=issue["createdAt"],
                    labels=[GitHubLabel(name=label["name"],
                                        description=label["description"],
                                        color=label["color"]) for label in issue["labels"]],
                    milestone=GitHubMilestone(number=issue["milestone"]["number"],
                                                title=issue["milestone"]["title"],
                                                description=issue["milestone"]["description"],
                                                due_on=issue["milestone"]["dueOn"]) if issue["milestone"] else None,
                    number=issue["number"],
                    project_cards=None,
                    reaction_groups=[GitHubReactionGroup(content=reaction["content"],
                                                        total_count=reaction["users"]["totalCount"]) for reaction in issue["reactionGroups"]],
                    state=issue["state"],
                    title=issue["title"],
                    updated_at=issue["updatedAt"],
                    url=issue["url"]
                ))
                session.add(github_issue)
                issues_list.append(github_issue)
        except Exception as e:
            session.rollback()
            print(e)
        else:
            session.commit()

    return issues_list

# This uses the files in json/reuse_ to populate the database
# It assumes that all the files in the directory are json files
# It assumes that the files are in the format of the GitHub API
# It assumes that the tables have already been created
def insert_github_prs(engine):
    files = [file for file in pathlib.Path("json/reuse").rglob("*prs.json")]
    with Session(engine) as session:
        file_names = []
        for file in tqdm(files):
            insert_github_pr(session, file, file_names)
        session.commit()

def unique_user_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist

def insert_github_pr(session: Session, file: pathlib.Path, file_names: list = []) -> list[GitHubPullRequest]:
    file_name = os.path.basename(file)
    if file_name in file_names:
        return []
    file_names.append(file_name)
    prs_list = []
    with open(file, "r") as json_file:
        prs = json.load(json_file)
        try:
            for pr in prs:
                github_pr = (GitHubPullRequest(
                    additions=pr["additions"],
                    assignees=[upsert_gh_user(session, assignee) for assignee in pr["assignees"]],
                    author=upsert_gh_user(session, pr["author"]),
                    base_ref_name=pr["baseRefName"],
                    body=pr["body"],
                    changed_files=pr["changedFiles"],
                    closed=pr["closed"],
                    closed_at=pr["closedAt"],
                    comments=[GitHubComment(author=upsert_gh_user(session, comment["author"]),
                                            author_association=comment["authorAssociation"],
                                            body=comment["body"],
                                            created_at=comment["createdAt"],
                                            includes_created_edit=comment["includesCreatedEdit"],
                                            is_minimized=comment["isMinimized"],
                                            minimized_reason=comment["minimizedReason"],
                                            reaction_groups=[GitHubReactionGroup(content=reaction["content"],
                                                        total_count=reaction["users"]["totalCount"]) for reaction in comment["reactionGroups"]]) for comment in pr["comments"]],
                    commits=[GitHubCommit(authored_date=commit["authoredDate"],
                                            authors=list(set([upsert_gh_user(session, author) for author in commit["authors"]])),
                                            committed_date=commit["committedDate"],
                                            message_body=commit["messageBody"],
                                            message_headline=commit["messageHeadline"],
                                            oid=commit["oid"]) for commit in pr["commits"]],
                    created_at=pr["createdAt"],
                    deletions=pr["deletions"],
                    files=[GitHubPullRequestFile(path=file["path"],
                                                    additions=file["additions"],
                                                    deletions=file["deletions"]) for file in pr["files"]] if pr["files"] else [],
                    head_ref_name=pr["headRefName"],
                    head_repository=GitHubRepository(name=pr["headRepository"]["name"]) if pr["headRepository"] else None,
                    head_repository_owner=upsert_gh_user(session, pr["headRepositoryOwner"]),
                    is_cross_repository=pr["isCrossRepository"],
                    is_draft=pr["isDraft"],
                    labels=[GitHubLabel(name=label["name"],
                                        description=label["description"],
                                        color=label["color"]) for label in pr["labels"]],
                    maintainer_can_modify=pr["maintainerCanModify"],
                    merge_commit=GitHubMergeCommit(commit=GitHubCommit(oid=pr["mergeCommit"]["oid"])) if pr["mergeCommit"] else None,
                    merge_state_status=pr["mergeStateStatus"],
                    mergeable=pr["mergeable"],
                    merged_at=pr["mergedAt"],
                    merged_by=upsert_gh_user(session, pr["mergedBy"]) if pr["mergedBy"] else None,
                    milestone=GitHubMilestone(number=pr["milestone"]["number"],
                                                title=pr["milestone"]["title"],
                                                description=pr["milestone"]["description"],
                                                due_on=pr["milestone"]["dueOn"]) if pr["milestone"] else None,
                    number=pr["number"],
                    potential_merge_commit=GitHubMergeCommit(commit=GitHubCommit(oid=pr["potentialMergeCommit"]["oid"])) if pr["potentialMergeCommit"] else None,
                    project_cards=None,
                    reaction_groups=[GitHubReactionGroup(content=reaction["content"],
                                                        total_count=reaction["users"]["totalCount"]) for reaction in pr["reactionGroups"]],
                    review_decision=pr["reviewDecision"],
                    review_requests=list(set([upsert_gh_user(session, review_request) for review_request in pr["reviewRequests"]])),
                    reviews=[GitHubReview(author=upsert_gh_user(session, review["author"]),
                                            author_association=review["authorAssociation"],
                                            body=review["body"],
                                            submitted_at=review["submittedAt"],
                                            includes_created_edit=review["includesCreatedEdit"],
                                            reaction_groups=[GitHubReactionGroup(content=reaction["content"],
                                                        total_count=reaction["users"]["totalCount"]) for reaction in review["reactionGroups"]],
                                            state=review["state"]) for review in pr["reviews"]],
                    state=pr["state"],
                    status_check_rollup=[GitHubStatusCheckRollup(name=status_check["name"],
                                                                    status=status_check["status"],
                                                                    conclusion=status_check["conclusion"],
                                                                    started_at=status_check["startedAt"],
                                                                    completed_at=status_check["completedAt"],
                                                                    details_url=status_check["detailsUrl"]) for status_check in pr["statusCheckRollup"]] if pr["statusCheckRollup"] else [],
                    title=pr["title"],
                    updated_at=pr["updatedAt"],
                    url=pr["url"]
                ))
                session.add(github_pr)
                prs_list.append(github_pr)
        except Exception as e:
            session.rollback()
        else:
            session.commit()
    return prs_list

def get_reuse_repos():
    reuse_repos = {}
    files = [file for file in pathlib.Path("json/reuse/").rglob("*.json")]
    files.sort()

    for file in files:
        file_name = os.path.basename(file)
        owner_repo = file_name.split("_detailed_")[0]
        owner = owner_repo.split("_")[0]
        repo = owner_repo.split("_")[1]
        if owner_repo not in reuse_repos:
            reuse_repos[owner_repo] = {"owner": owner,
                                        "name": repo,
                                        }
        if "detailed_issues" in file_name:
            reuse_repos[owner_repo]["issues"] = file
        elif "detailed_prs" in file_name:
            reuse_repos[owner_repo]["prs"] = file

    print(len(reuse_repos))
    return reuse_repos

def insert_reuse_repos(engine):
    reuse_repos = get_reuse_repos()
    reuse_repo_list = []
    with Session(engine) as session:
        for repo in tqdm(reuse_repos.values()):
            reuse_repo = insert_reuse_repo(session, repo)
            reuse_repo_list.append(reuse_repo)
        session.commit()
    return reuse_repo_list

def insert_reuse_repo(session: Session, reuse_repo: dict) -> ReuseRepository:
    owner = reuse_repo["owner"]
    repo = reuse_repo["name"]
    issues = insert_github_issue(session, reuse_repo["issues"]) if "issues" in reuse_repo else []
    prs = insert_github_pr(session, reuse_repo["prs"]) if "prs" in reuse_repo else []
    reuse_repo = (ReuseRepository(
        name=repo,
        owner=owner,
        url=f"github.com/{owner}/{repo}",
        issues=issues,
        pull_requests = prs,
        files = []
    ))
    try:
        session.add(reuse_repo)
    except Exception as e:
        print(e)
        session.rollback()
    else:
        return reuse_repo

def upsert_reuse_repository(session: Session, data: dict) -> ReuseRepository:
    obj = session.query(ReuseRepository).filter(ReuseRepository.name == data.get("name"),
                                                ReuseRepository.owner == data.get("owner")).first()
    if not obj:
        obj = insert_reuse_repo(session, data)
        session.add(obj)
    return obj

def upsert_model(session, model_context_id, model_hub_id):
    model = session.query(Model).filter(Model.context_id == model_context_id,
                                        Model.model_hub_id == model_hub_id).first()
    if not model:
        model = Model(context_id = model_context_id, model_hub_id = model_hub_id)
        session.add(model)
        session.commit()
    return model

def link_ptm_gh(engine):
    files = pathlib.Path('json/ptm_to_gh').glob('*.json')
    with Session(engine) as session:
        for link_file in files:
            link_file_str = str(link_file)
            model_hub_id = 1 if "hf" in link_file_str else 2
            with open(link_file, "r") as json_file:
                links : dict = json.load(json_file)
                for model_context_id in tqdm(links.keys()):
                    model : Model = upsert_model(session, model_context_id, model_hub_id)
                    reuse_repos = []
                    total_usage = len(links[model_context_id]["usage_repository"])
                    model.reuse_amount = total_usage
                    reuse_files = {}
                    for file in links[model_context_id]["file_path"]:
                        owner_name = "/".join([file.split("_")[0], file.split("/")[1]])
                        if owner_name not in reuse_files:
                            reuse_files[owner_name] = []
                        reuse_files[owner_name].append(file)
                    for repo_url in links[model_context_id]["usage_repository"]:
                        repo = {}
                        repo["url"] = repo_url
                        owner_name = repo_url.split("/", 1)[1]
                        repo["owner"] = owner_name.split("/")[0]
                        repo["name"] = owner_name.split("/")[1]
                        reuse_repo : ReuseRepository = upsert_reuse_repository(session, repo)
                        # print(f"Model Context ID: {model_context_id}")
                        # print(f"Reuse Repo Owner_name: {owner_name}")
                        # print(f"Reuse File Owner_names {reuse_files.keys()}")
                        # print(f"Owner_name in reuse_files: {owner_name in reuse_files}")
                        if reuse_files.get(owner_name):
                            for file in reuse_files.get(owner_name):
                                reuse_file = ReuseFile(path=file, model=model, reuse_repository=reuse_repo)
                                # print(reuse_file.model)
                                session.add(reuse_file)
                        # raise Exception
                        reuse_repos.append(reuse_repo)
                    model.reuse_repositories = reuse_repos
                    session.commit()

def insert_model_hubs(engine):
    with Session(engine) as session:
        model_hubs = [ModelHub(name="HuggingFace", url="https://huggingface.co/"),
                        ModelHub(name="PyTorch", url="https://pytorch.org")]
        session.add_all(model_hubs)
        session.commit()

def get_all_github_prs(session: Session, repo_url: str) -> list[GitHubPullRequest]:
    return session.query(GitHubPullRequest).filter(GitHubPullRequest.url.contains(repo_url)).all()

def get_all_github_issues(session: Session, repo_url: str) -> list[GitHubIssue]:
    return session.query(GitHubIssue).filter(GitHubIssue.url.contains(repo_url)).all()

def upsert_ptm_pull_requests(session: Session, repo_url: String) -> PTMPullRequests:
    obj = session.query(PTMPullRequests).filter(PTMPullRequests.repo_url == repo_url).first()
    if not obj:
        obj = PTMPullRequests(repo_url=repo_url,
                                pull_requests=get_all_github_prs(session, repo_url))
        session.add(obj)
    return obj

def upsert_ptm_issues(session: Session, repo_url: String) -> PTMIssues:
    obj = session.query(PTMIssues).filter(PTMIssues.repo_url == repo_url).first()
    if not obj:
        obj = PTMIssues(repo_url=repo_url,
                                issues=get_all_github_issues(session, repo_url))
        session.add(obj)
    return obj

def insert_pt_models(engine, pt_model_file = "json/models/PT_model_issues_prs_formatted.json"):
    with Session(engine) as session:
        with open(pt_model_file, "r") as json_file:
            dicts = json.load(json_file)
            length = len(list(dicts))
        with open(pt_model_file, "r") as json_file:
            dicts = json.load(json_file)
            for row in tqdm(dicts, total=length):
                try:
                    # print(f"Discussions keys: {literal_eval(row['discussions'])}") if row["discussions"] else None
                    session.add(Model(context_id=row["context_id"],
                                    model_hub_id=2,
                                    repo_url=row["repo_url"],
                                    authors=[upsert(session, Author, row["author"])],
                                    licenses=[upsert(session, License, row["license"])],
                                    has_snapshot=True,
                                    ptm_issues=upsert_ptm_issues(session, row["repo_url"]),
                                    ptm_pull_requests=upsert_ptm_pull_requests(session, row["repo_url"]),
                                    tags=[upsert(session, Tag, tag) for tag in row.get("tags", [])]
                                    ))
                except Exception as e:
                    print(row["context_id"])
                    raise e
                else:
                    session.commit()

def insert_pt_blobs(engine, file = "reuse_repos_temp.csv"):
    with Session(engine) as session:
        with open(file, "r") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            length = len(list(reader))
        with open(file, "r") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            for row in tqdm(reader, total=length):
                try:
                    issue_or_pr = GitHubPRIssueBlob(blob=upsert_gh_blob(session, row["repo_url"]),
                                                    type=row["issue_or_pr"],
                                                    gh_pr_issue=row["value"])
                    session.add(issue_or_pr)
                except Exception as e:
                    print(row["repo_url"])
                    print(e)
                session.commit()

if __name__ == "__main__":
    engine = create_engine("sqlite:///PeaTMOSS_NEW.db")

    # BASE.metadata.drop_all(engine)
    # BASE.metadata.create_all(engine)

    # insert_github_prs(engine)
    # insert_github_issues(engine)
    # insert_reuse_repos(engine)
    # insert_model_hubs(engine)
    # insert_pt_models(engine)
    # insert_hf_models(engine)
    # link_ptm_gh(engine)
    # Get the top 10 models by total links to GitHub, as well as the discussions for each model,
    # the reuse repositories they are associated with, and the files in those repositories, as well
    # as the pull requests and issues of the reuse repositories
    # A models links to github are described in the table model_to_reuse_repository
    # Do all this by querying the database
