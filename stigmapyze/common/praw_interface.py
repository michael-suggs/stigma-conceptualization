from typing import List

from praw.models import Comment
from praw.models.comment_forest import CommentForest

from .reddit_post import RedditComment


def parse_comment_forest(cf: CommentForest) -> List[RedditComment]:
    for comment in CommentForest
