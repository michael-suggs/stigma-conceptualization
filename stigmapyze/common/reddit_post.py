import json
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Generator, List, TextIO, Tuple

from praw.models import Comment
from praw.models.comment_forest import CommentForest


class RedditComment:
    id: str
    body: str
    is_root: bool
    is_submitter: str
    parent_id: str
    score: int
    replies: Dict[str, RedditComment]

    def __init__(self, comment: Comment) -> None:
        self.id = comment.id
        self.body = comment.body
        self.is_submitter = comment.is_submitter
        self.parent_id = comment.parent_id
        self.score = comment.score
        self.replies = ... # TODO finish this

    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        pass

    @staticmethod
    def parse_comments(comments: List[Comment]) -> List[RedditComment]:
        ...


@dataclass
class RedditPost:
    """Class holding info parsed from an individual Reddit post.

    Attributes:
        id (str): The post's ID (unique; defined by Reddit).
        title (str): The post's title.
        text (str): Body text of the original post.
        comments (CommentForest): A praw CommentForest instance containing
            all top-level comments and their replies.
    """
    id: str
    title: str
    text: str
    comments: CommentForest

    def __repr__(self) -> str:
        return json.dumps({
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'comments': self.comments.list()
        })

    def __str__(self) -> str:
        return json.dumps({
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'comments': self.comments.list()
        }, indent=4)

    def get_top_level_comments(self) -> Generator[Tuple[str, str], None, None]:
        """Yields all top-level comments for this post.

        Yields:
            Generator[Tuple[str, str]]: A generator object returning tuples
            in the form of (id, body) where "id" refers to the comment's
            unique identifier string and "body" contains the body text of the
            comment itself.
        """
        for comment in self.comments:
            yield (comment.id, comment.body)

    def get_flattened_comments(self) -> List[Comment]:
        """Flattens all comments and replies into a list.

        Returns:
            List[Comment]: A list of praw Comment objects in order. Comments
            are flattened so that all replies to comments (both top-level and
            nested) are present in a single-dimensional list.
        """
        return self.comments.list()

    def write_post(self, fp: TextIO, top_level_only: bool = False) -> None:
        """Writes a post to a given file.

        Parameters
        ----------
        fp : TextIo
            A pointer to the file to write (json dumps) to.
        top_level_only : bool, optional
            If True, only writes the top-level comments. By default False.
        """
        comments = (list(self.get_top_level_comments()) if top_level_only
            else self.get_flattened_comments())
        json.dump({
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'comments': comments
        }, fp, indent=4)
