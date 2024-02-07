from dataclasses import dataclass
import datetime
from typing import NewType

CommentText = NewType("CommentText", str)
RepositoryName = NewType("RepositoryName", str)
CommentType = NewType("CommentType", str)

@dataclass
class GitHubComment:
    date: datetime.datetime
    text: CommentText
    repository: RepositoryName
    comment_type: CommentType


def fetch_comments(handle: str) -> list[GitHubComment]:
    """
    Fetch all GitHub comments authored by user `handle`
    """
    ...
