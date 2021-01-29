from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Dict, Generator, List, TextIO, Tuple

from praw.models import Comment
from praw.models.comment_forest import CommentForest
from praw.models.reddit.submission import Submission


class RedditComment:
    id: str
    depth: int
    body: str
    is_root: bool
    is_submitter: str
    parent_id: str
    score: int
    replies: List[RedditComment]

    def __init__(self, comment: Comment, depth: int) -> None:
        self.id = comment.id
        self.depth = depth
        self.body = comment.body
        self.is_submitter = comment.is_submitter
        self.parent_id = comment.parent_id
        self.score = comment.score
        self.replies = ... # TODO finish this

    def __repr__(self) -> str:
        return json.dumps({
            'id': self.id,
            'body': self.body,
            'is_root': self.is_root,
            'is_submitter': self.is_submitter,
            'parent_id': self.parent_id,
            'score': self.score,
            'replies': self.replies
        })

    def __str__(self) -> str:
        return json.dumps({
            'id': self.id,
            'body': self.body,
            'is_root': self.is_root,
            'is_submitter': self.is_submitter,
            'parent_id': self.parent_id,
            'score': self.score,
            'replies': self.replies
        }, indent=4)

    @staticmethod
    def parse_replies(replies: CommentForest) -> List[RedditComment]:
        # TODO not yet implemented
        ...

    @staticmethod
    def _parse_replies(replies: List[Comment]):
        ...


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

    def __init__(self, post: Submission) -> None:
        self.id = post.id
        self.title = post.title
        self.text = post.selftext
        self.comments = post.comments

        post_id = f't3_{self.id}'
        non_root = list(filter(lambda x: not x.is_root, self.comments))

        self.comments = [RedditPost.comments_to_json(c, non_root) for c in
            self.comments if post_id == c.parent_id]

    def __repr__(self) -> str:
        return json.dumps({
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'comments': self.comments
        })

    def __str__(self) -> str:
        return json.dumps({
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'comments': self.comments
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
        # comments = [RedditPost.comments_to_json(c, self.comments) for c in
        #         self.comments if f't3_{c.parent_id}' == self.id]

        json.dump({
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'comments': self.comments
        }, fp, indent=4, ensure_ascii=False)

    @staticmethod
    def comments_to_json(comment: Comment, replies: List[Comment]) -> str:
        children = [RedditPost.comments_to_json(child, replies) for child in
            filter(lambda c: f't1_{c.parent_id}' == comment.id, replies)]

        return {
            'id': comment.id,
            'body': comment.body,
            'is_root': comment.is_root,
            'is_submitter': comment.is_submitter,
            'parent_id': comment.parent_id,
            'score': comment.score,
            'replies': children
        }
