import json
from collections import namedtuple
from typing import Union

import praw


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


def connect_and_configure(config_file: str):
    config = Config(config_file)
    reddit_conn = praw.Reddit(
        client_id=f'{config.client_id}',
        client_secret=f'{config.client_secret}',
        user_agent=f'{config.user_agent}',
        redirect_uri=f'{config.redirect_uri}'
    )



