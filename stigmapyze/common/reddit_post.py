import json
from dataclasses import dataclass
from typing import Generator, List, Tuple

from praw.models.comment_forest import Comment, CommentForest


@dataclass
class RedditPost:
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

    def get_top_level_comments(self) -> Generator[Tuple[str, str]]:
        for comment in self.comments:
            yield (comment.id, comment.body)

    def get_flattened_comments(self) -> List[Comment]:
        return self.comments.list()
