import datetime as dt
import json
from collections import namedtuple
from functools import singledispatch
from typing import List, Union

import praw
from praw.models.comment_forest import CommentForest, Comment


@dataclass(frozen=True, init=False)
class Config:
    """Config class for PRAW instance.

    Attributes:
        client_id:
        client_secret:
        user_agent:
        redirect_uri:
    """
    client_id: str
    client_secret: str
    user_agent: str
    redirect_uri: str

    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            js = json.load(f)
            self.client_id = js['client_id']
            self.client_secret = js['client_secret']
            self.user_agent = js['user_agent']
        self.redirect_uri = 'http://localhost:8080'


@dataclass
class RedditPost:
    id: str
    title: str
    text: str
    comments: CommentForest


def connect_and_configure(config_file: str) -> praw.Reddit:
    config = Config(config_file)
    reddit_conn = praw.Reddit(
        client_id=f'{config.client_id}',
        client_secret=f'{config.client_secret}',
        user_agent=f'{config.user_agent}'
    )

    return reddit_conn


@singledispatch
def parse_subreddit(
    post_limit: int,
    reddit_conn: praw.Reddit,
    sub_name: str = 'SuicideWatch'
):
    posts: List[RedditPost] = []
    subreddit = reddit_conn.subreddit(sub_name)

    for post in subreddit.new(limit=post_limit):
        posts.append(RedditPost(
            id = post.id,
            title = post.title,
            text = post.selftext,
            comments = post.comments
        ))



@parse_subreddit.register
def _(
    post_limit: dt.timedelta,
    reddit_conn: praw.Reddit,
    sub_name: str = 'SuicideWatch'
):
    ...
