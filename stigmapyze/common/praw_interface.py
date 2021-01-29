import json
from typing import List

from praw.models import Comment
from praw.models.comment_forest import CommentForest

from .reddit_post import RedditComment


def comment_to_json(comment: Comment) -> str:
    if not comment.replies:
        replies = []
    else:
        replies: List[str] = [comment_to_json(reply)
            for reply in comment.replies]

    return json.dumps({
        'id': comment.id,
        'body': comment.body,
        'is_root': comment.is_root,
        'is_submitter': comment.is_submitter,
        'parent_id': comment.parent_id,
        'score': comment.score,
        'replies': replies
    }, indent=4)
