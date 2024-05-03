import dataclasses
from dataclasses import dataclass
import datetime
import json
import dateutil.parser
import os
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

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if token := os.getenv("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"token {token}"

def extract_next_page_link_from_header(link_header: str) -> str | None:
    """
    Extract the URL of the next page of results from the "Link" header
    """
    # The "link" header contains a comma-separated list of links, each with a
    # "rel" attribute (separated from the link by a semicolon and a space) that
    # describes the relationship of the link to the current page of results.
    # We're interested in the "rel=next" link.
    # If there is no "rel=next" link, we're done.
    links = link_header.split(", ")
    for link in links:
        url, rel = link.split("; ")
        if rel == 'rel="next"':
            # The URL is enclosed in angle brackets, so we strip those off
            return url.lstrip("<").rstrip(">")
    return None

def send_query(url: str, query: str) -> list[dict]:
    """
    Send a query to the GitHub API and return the `items` field of the response
    """
    items = []
    current_url = f"{url}?q={query}&per_page=30"
    while current_url:
        # The GitHub Search API uses pagination, so we need to fetch multiple
        # pages of results. The current page to fetch is determined by the
        # `current_url` variable.
        response = requests.get(current_url, headers=HEADERS)
        response.raise_for_status()
        items.extend(response.json()["items"])

        # Pagination: GitHub API responses contain a "link" header that
        # contains links to the next page of results. If there is no "link"
        # header, we're done.
        if "link" not in response.headers:
            break
        # If there is a "link" header, extract the URL of the next page of
        # results.
        current_url = extract_next_page_link_from_header(response.headers["link"])

    return items

def get_latest_action(comment_json: dict) -> (str, str):
    min_date = "1970-01-01T00:00:00Z"
    created = ("created", comment_json.get("created_at") or min_date)
    updated = ("updated", comment_json.get("updated_at") or min_date)
    closed = ("closed", comment_json.get("closed_at") or min_date)
    actions = [created, updated, closed]
    actions = sorted(actions, key=lambda x: dateutil.parser.parse(x[1]))
    return actions[-1]


def fetch_issues(handle: str, lower_date: datetime.datetime, upper_date: datetime.datetime) -> list[GitHubComment]:
    """
    Fetch all GitHub issues authored by user `handle`
    """
    # TODO: could also try to use "updated_at" or "closed_at" fields
    datetime_filter = f"created:{to_github_datetime_format(lower_date)}..{to_github_datetime_format(upper_date)}"
    response_items = send_query(f"{BASE_URL}/issues", f"is:issue+author:{handle}+{datetime_filter}")
    all_comments = []
    for comment_json in response_items:
        latest_action, date = get_latest_action(comment_json)
        all_comments.append(
            GitHubComment(
                dateutil.parser.parse(date),
                CommentText(comment_json["body"]),
                # example repo URL: https://api.github.com/repos/tweag/chainsail
                # so we use "tweag/chainsail" as human-readable repo identifier
                RepositoryName("/".join(comment_json["repository_url"].split("/")[-2:])),
                latest_action
            )
        )
    return all_comments

def fetch_prs(handle: str, lower_date: datetime.datetime, upper_date: datetime.datetime) -> list[GitHubComment]:
    """
    Fetch all GitHub pull requests authored by user `handle`
    """
    # TODO: could also try to use "updated_at" or "closed_at" fields
    datetime_filter = f"created:{to_github_datetime_format(lower_date)}..{to_github_datetime_format(upper_date)}"
    response_items = send_query(f"{BASE_URL}/issues", f"is:pull-request+author:{handle}+{datetime_filter}")
    all_comments = []
    for comment_json in response_items:
        latest_action, date = get_latest_action(comment_json)
        all_comments.append(
            GitHubComment(
                dateutil.parser.parse(date),
                CommentText(comment_json["body"]),
                # example repo URL: https://api.github.com/repos/tweag/chainsail
                # so we use "tweag/chainsail" as human-readable repo identifier
                RepositoryName("/".join(comment_json["repository_url"].split("/")[-2:])),
                latest_action
            )
        )
    return all_comments

def fetch_commits(handle: str, lower_date: datetime.datetime, upper_date: datetime.datetime) -> list[GitHubComment]:
    """
    Fetch all GitHub commits authored by user `handle`
    """
    datetime_filter = f"author-date:{to_github_datetime_format(lower_date)}..{to_github_datetime_format(upper_date)}"
    response_items = send_query(f"{BASE_URL}/commits", f"author:{handle}+committer:{handle}+{datetime_filter}")
    return [
        GitHubComment(
            dateutil.parser.parse(comment_json["commit"]["author"]["date"]),
            CommentText(comment_json["commit"]["message"]),
            RepositoryName(comment_json["repository"]["full_name"]),
            "committed"
        )
        for comment_json in response_items
    ]


def fetch_comments(handle: str, lower_date: datetime.datetime, upper_date: datetime.datetime) -> list[GitHubComment]:
    """
    Fetch all GitHub comments authored by user `handle`
    """
    all_comments = []
    all_comments.append(fetch_issues(handle, lower_date, upper_date))
    all_comments.append(fetch_prs(handle, lower_date, upper_date))
    all_comments.append(fetch_commits(handle, lower_date, upper_date))
    return all_comments

if __name__ == "__main__":
    lower_date = datetime.datetime.now() - datetime.timedelta(days=7)
    upper_date = datetime.datetime.now()

    comments = fetch_comments("simeoncarstens", lower_date, upper_date)
    # Flatten list: why does this work? https://stackoverflow.com/a/952946/1656472
    # Tweag style!
    comments = sum(comments, [])
    # Without `default=str`, `dumps` will fail on `datetime` objects
    print(json.dumps(list(map(dataclasses.asdict, comments)), default=str))
