import datetime as dt
import json
from dataclasses import dataclass
from functools import singledispatch
from typing import List, Generator

import praw

from ..common.reddit_post import RedditPost


@dataclass(init=False)
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


def connect_and_configure(config_file: str) -> praw.Reddit:
    """Creates a praw connection using info from a config.json file.

    Args:
        config_file (str): Path to the Reddit (praw) configuration file.

    Returns:
        praw.Reddit: A connected Reddit instance.
    """
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
) -> Generator[RedditPost, None, None]:
    """Parses a desired number of posts and comments from a given subreddit.

    Args:
        post_limit (int): Maximum number of posts to parse.
        reddit_conn (praw.Reddit): The praw Reddit connection to use.
        sub_name (str, optional): The subreddit to parse.
            Defaults to 'SuicideWatch'.

    Returns:
        List[RedditPost]: A list of parsed post objects containing the title,
            text, and the post's CommentForest object containing all comments.
    """
    subreddit = reddit_conn.subreddit(sub_name)

    for post in subreddit.top(limit=post_limit):
        yield RedditPost(post)


@parse_subreddit.register
def _(
    post_limit: dt.timedelta,
    reddit_conn: praw.Reddit,
    sub_name: str = 'SuicideWatch'
) -> Generator[RedditPost, None, None]:
    """Dispatched method for `parse_subreddit` with a timedelta instead.

    Parses posts (and their respective comments) from within a given timeframe
    (timedelta) from the current time. The number of posts parsed will thus be
    dependent on the activity level of the subreddit accessed--subreddits with
    more activity will return a higher number of posts for a given timeframe
    than those with less.

    Args:
        post_limit (dt.timedelta): Time to subtract from the present moment to
            determine the oldest posts to parse.
        reddit_conn (praw.Reddit): The praw Reddit connection to use.
        sub_name (str, optional): The subreddit to parse.
            Defaults to 'SuicideWatch'.

    Returns:
        List[RedditPost]: A list of parsed post objects containing the title,
            text, and the post's CommentForest object containing all comments.
    """
    subreddit = reddit_conn.subreddit(sub_name)
    # posts: List[RedditPost] = []
    post_limit = (dt.datetime.utcnow() - post_limit)

    for post in subreddit.new():
        post_utc = dt.datetime.utcfromtimestamp(post.created_utc)
        if post_utc < post_limit:
            break

        yield RedditPost(post)
