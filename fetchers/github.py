from dataclasses import dataclass
import datetime
import dateutil.parser
import requests
from typing import Literal, NewType

CommentText = NewType("CommentText", str)
RepositoryName = NewType("RepositoryName", str)
CommentType = NewType("CommentType", str)
Action = Literal["created", "updated", "closed", "reopened", "merged", "commented", "committed"]

@dataclass
class GitHubComment:
    date: datetime.datetime
    text: CommentText
    repository: RepositoryName
    action: Action


def to_github_datetime_format(dt: datetime.datetime) -> str:
    """
    Convert a datetime object to the format used by GitHub's API
    """
    return dt.isoformat()[:-7] + "Z"

BASE_URL = "https://api.github.com/search"
DATETIME_LOWER_BOUND = (datetime.datetime.now() - datetime.timedelta(days=31))
DATETIME_UPPER_BOUND = datetime.datetime.now()

def get_latest_action(comment_json: dict) -> (str, str):
    min_date = "1970-01-01T00:00:00Z"
    created = ("created", comment_json.get("created_at") or min_date)
    updated = ("updated", comment_json.get("updated_at") or min_date)
    closed = ("closed", comment_json.get("closed_at") or min_date)
    actions = [created, updated, closed]
    actions = sorted(actions, key=lambda x: dateutil.parser.parse(x[1]))
    return actions[-1]


def fetch_issues(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub issues authored by user `handle`
    """
    # TODO: could also try to use "updated_at" or "closed_at" fields
    datetime_filter = f"created:{to_github_datetime_format(DATETIME_LOWER_BOUND)}..{to_github_datetime_format(DATETIME_UPPER_BOUND)}"
    response = requests.get(f"{BASE_URL}/issues?q=is:issue+author:{handle}+{datetime_filter}")
    all_comments = []
    for comment_json in response.json()["items"]:
        latest_action, date = get_latest_action(comment_json)
        all_comments.append(
            GitHubComment(
                date,
                CommentText(comment_json["body"]),
                # example repo URL: https://api.github.com/repos/tweag/chainsail
                # so we use "tweag/chainsail" as human-readable repo identifier
                RepositoryName("/".join(comment_json["repository_url"].split("/")[-2:])),
                latest_action
            )
        )
    return all_comments

def fetch_prs(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub pull requests authored by user `handle`
    """
    # TODO: could also try to use "updated_at" or "closed_at" fields
    datetime_filter = f"created:{to_github_datetime_format(DATETIME_LOWER_BOUND)}..{to_github_datetime_format(DATETIME_UPPER_BOUND)}"
    response = requests.get(f"{BASE_URL}/issues?q=is:pull-request+author:{handle}+{datetime_filter}")
    all_comments = []
    for comment_json in response.json()["items"]:
        latest_action, date = get_latest_action(comment_json)
        all_comments.append(
            GitHubComment(
                date,
                CommentText(comment_json["body"]),
                # example repo URL: https://api.github.com/repos/tweag/chainsail
                # so we use "tweag/chainsail" as human-readable repo identifier
                RepositoryName("/".join(comment_json["repository_url"].split("/")[-2:])),
                latest_action
            )
        )
    return all_comments

def fetch_commits(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub commits authored by user `handle`
    """
    datetime_filter = f"author-date:{to_github_datetime_format(DATETIME_LOWER_BOUND)}..{to_github_datetime_format(DATETIME_UPPER_BOUND)}"
    response = requests.get(f"{BASE_URL}/commits?q=author:{handle}+committer:{handle}+{datetime_filter}")
    return [
        GitHubComment(
            dateutil.parser.parse(comment_json["commit"]["author"]["date"]),
            CommentText(comment_json["commit"]["message"]),
            RepositoryName(comment_json["repository"]["full_name"]),
            "committed"
        )
        for comment_json in response.json()["items"]
    ]


def fetch_comments(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub comments authored by user `handle`
    """
    all_comments = []
    all_comments.append(fetch_issues(handle))
    all_comments.append(fetch_prs(handle))
    all_comments.append(fetch_commits(handle))
    return all_comments

if __name__ == "__main__":
    print(fetch_comments("simeoncarstens")[:10])
