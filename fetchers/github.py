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


BASE_URL = "https://api.github.com/search"

def fetch_issue_comments(handle: str) -> list[GitHubComment]:
    response = requests.get(f"{BASE_URL}/issues?q=commenter:{handle}")
    return [
        GitHubComment(
            # use datetime string of form "YYYY-MM-DDTHH:MM:SSZ" and convert into datetime object
            # TODO: could also try to use "updated_at" or "closed_at" fields
            dateutil.parser.parse(comment_json["created_at"]),
            CommentText(comment_json["body"]),
            # example repo URL: https://api.github.com/repos/tweag/chainsail
            # so we use "tweag/chainsail" as human-readable repo identifier
            RepositoryName("/".join(comment_json["repository_url"].split("/")[-2:]))
        )

        for comment_json in response.json()["items"]
    ]

def fetch_comments(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub comments authored by user `handle`
    """
    all_comments = []
    all_comments.append(fetch_issue_comments(handle))
    return all_comments

if __name__ == "__main__":
    print(fetch_comments("simeoncarstens")[:10])
