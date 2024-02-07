from dataclasses import dataclass
import datetime
import dateutil.parser
import requests
from typing import NewType

CommentText = NewType("CommentText", str)
RepositoryName = NewType("RepositoryName", str)
CommentType = NewType("CommentType", str)

@dataclass
class GitHubComment:
    date: datetime.datetime
    text: CommentText
    repository: RepositoryName


def to_github_datetime_format(dt: datetime.datetime) -> str:
    """
    Convert a datetime object to the format used by GitHub's API
    """
    return dt.isoformat()[:-7] + "Z"

BASE_URL = "https://api.github.com/search"
DATETIME_LOWER_BOUND = (datetime.datetime.now() - datetime.timedelta(days=7))
DATETIME_UPPER_BOUND = datetime.datetime.now()
# TODO: could also try to use "updated_at" or "closed_at" fields
DATETIME_FILTER = f"created:<{to_github_datetime_format(DATETIME_UPPER_BOUND)}+created:>{to_github_datetime_format(DATETIME_LOWER_BOUND)}"

def fetch_issues(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub issues authored by user `handle`
    """
    response = requests.get(f"{BASE_URL}/issues?q=is:issue+author:{handle}+{DATETIME_FILTER}")
    return [
        GitHubComment(
            dateutil.parser.parse(comment_json["created_at"]),
            CommentText(comment_json["body"]),
            # example repo URL: https://api.github.com/repos/tweag/chainsail
            # so we use "tweag/chainsail" as human-readable repo identifier
            RepositoryName("/".join(comment_json["repository_url"].split("/")[-2:]))
        )

        for comment_json in response.json()["items"]
    ]

def fetch_prs(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub pull requests authored by user `handle`
    """
    response = requests.get(f"{BASE_URL}/issues?q=is:pull-request+author:{handle}+{DATETIME_FILTER}")
    return [
        GitHubComment(
            dateutil.parser.parse(comment_json["created_at"]),
            CommentText(comment_json["body"]),
            RepositoryName("/".join(comment_json["repository_url"].split("/")[-2:]))
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
    return all_comments

if __name__ == "__main__":
    print(fetch_comments("simeoncarstens")[:10])
