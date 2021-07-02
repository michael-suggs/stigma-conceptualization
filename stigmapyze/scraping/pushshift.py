from dataclasses import dataclass
from datetime import datetime
from enum import Enum, Flag, auto

import pandas as pd
import re
import requests
from time import sleep
from typing import Any, Dict, Final, Generator, List, Literal, Optional, Tuple, Union, overload

from ..common.reddit import Comment, Submission

BASEURL: Final[str] = 'https://api.pushshift.io/reddit'
ERRLIMIT: Final[int] = 15


class PushshiftException(Exception):
    ...


class PSFlag(Flag):
    OK = auto()
    DONE = auto()
    HTTPERROR = auto()
    SUBMLENERROR = auto()


@dataclass
class PSReturn:
    date: Union[int, datetime]
    flag: PSFlag
    _errcount: int = 0


class Endpoint(Enum):
    COMMENT = f'{BASEURL}/search/comment'
    SUBMISSION = f'{BASEURL}/search/submission'
    SUBMCOMMENTS = f'{BASEURL}/submission/comment_ids'

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return f'{self.value}/' + str(*args)


def check_loop_err(err: PSReturn, flag: PSFlag, submissions: List[Submission]):
    if err and err.flag == PSFlag.HTTPERROR:
        if err._errcount == ERRLIMIT:
            if submissions:
                return submissions, PSReturn(submissions[-1].created_utc, PSFlag.HTTPERROR)
            else:
                return submissions, PSReturn(None, PSFlag.HTTPERROR)
        err._errcount += 1
    else:
        err = PSReturn(None, PSFlag.HTTPERROR, 1)


def query_comments(
    q: str = None,
    ids: List[str] = None,
    size: int = 25,
    fields: Union[str, List[str]] = None,
    sort: Literal["asc", "desc"] = "desc",
    sort_type: Literal["score", "num_comments", "created_utc"] = "created_utc",
    aggs: Literal["author", "link_id", "created_utc", "subreddit"] = None,
    author: str = None,
    subreddit: str = None,
    after: datetime = None,
    before: datetime = None,
    frequency: Literal["second", "minute", "hour", "day"] = None,
    metadata: bool = False,
) -> Dict[str, dict]:
    formatted_params: List[str] = list(
        filter(
            lambda l: l,
            [
                f'q={q}' if q else None,
                f'ids={",".join(ids)}' if ids else None,
                f'size={size}',
                f'fields={",".join(fields)}' if fields else None,
                f'sort={sort}',
                f'sort_type={sort_type}',
                f'aggs={aggs}',
                f'author={author}' if author else None,
                f'subreddit={subreddit}' if subreddit else None,
                f'after={after}' if after else None,
                f'before={before}' if before else None,
                f'frequency={frequency}' if frequency else None,
                f'metadata={metadata}',
            ]
        )
    )
    param_str: str = f'?{"&".join(formatted_params)}'
    query: str = Endpoint.COMMENT(param_str)
    err: PSReturn = None

    while True:
        resp = requests.get(query)
        if resp.status_code != 200:
            if err and err.flag == PSFlag.HTTPERROR:
                if err._errcount == ERRLIMIT:
                    raise ConnectionRefusedError(
                        f'HTTP {resp.status_code}: {query}'
                    )
                err._errcount += 1
            else:
                err = PSReturn(None, PSFlag.HTTPERROR, 1)
            print(f'HTTP {resp.status_code} {err._errcount}/{ERRLIMIT}')
            sleep(5)
            continue
        else:
            break

    data = resp.json()['data']
    comments: Dict = {s['id']: s for s in data}
    return comments


def query_submission_comments(submission_id: str) -> Dict[str, dict]:
    err: PSReturn = None
    query = Endpoint.SUBMCOMMENTS(submission_id)
    while True:
        resp = requests.get(query)
        if resp.status_code != 200:
            if err and err.flag == PSFlag.HTTPERROR:
                if err._errcount == ERRLIMIT:
                    raise ConnectionRefusedError(
                        f'HTTP {resp.status_code}: {query}'
                    )
                err._errcount += 1
            else:
                err = PSReturn(None, PSFlag.HTTPERROR, 1)
            print(f'HTTP {resp.status_code} {err._errcount}/{ERRLIMIT}')
            sleep(5)
            continue
        else:
            break

    comments = list(
        query_comments(ids=[id for id in resp.json()['data']]).values()
    )
    # comments = {id: query_comments(id)[id] for id in resp.json()['data']}
    return comments


def query_submissions(
    q: str = None,
    q_not: str = None,
    ids: List[str] = None,
    title: str = None,
    title_not: str = None,
    selftext: str = None,
    selftext_not: str = None,
    size: int = 25,
    fields: Union[str, List[str]] = None,
    sort: Literal["asc", "desc"] = "asc",
    sort_type: Literal["score", "num_comments", "created_utc"] = "created_utc",
    aggs: Literal["author", "link_id", "created_utc", "subreddit"] = None,
    author: str = None,
    subreddit: str = None,
    after: datetime = None,
    before: datetime = None,
    score: str = None,
    frequency: Literal["second", "minute", "hour", "day"] = None,
    metadata: bool = False,
    with_comments: bool = True,
) -> Generator[Submission, None, None]:
    before = int(datetime.utcnow().timestamp()) if not before else before
    formatted_params: List[str] = list(
        filter(
            lambda l: l,
            [
                f'q={q}' if q else None,
                f'q:not={q_not}' if q_not else None,
                f'ids={",".join(ids)}' if ids else None,
                f'title={title}' if title else None,
                f'title:not={title_not}' if title_not else None,
                f'selftext={selftext}' if selftext else None,
                f'selftext:not={selftext_not}' if selftext_not else None,
                f'size={size}',
                f'fields={",".join(fields)}' if fields else None,
                f'sort={sort}',
                f'sort_type={sort_type}',
                f'aggs={aggs}' if aggs else None,
                f'author={author}' if author else None,
                f'subreddit={subreddit}' if subreddit else None,
                f'after={after}' if after else None,
                f'before={before}' if before else None,
                f'score={score}' if score else None,
                f'frequency={frequency}' if frequency else None,
                f'metadata={metadata}',
            ]
        )
    )

    submissions: List[Submission] = []
    param_str: str = f'?{"&".join(formatted_params)}'
    err: Optional[PSReturn] = None
    prev_time = datetime.now()

    while True:
        query: str = Endpoint.SUBMISSION(param_str)
        data = requests.get(query)
        if data.status_code != 200:
            if err and err.flag == PSFlag.HTTPERROR:
                if err._errcount == ERRLIMIT:
                    raise ConnectionRefusedError(
                        f'HTTP {data.status_code}: {submissions[-1].created_utc}'
                    )
                err._errcount += 1
            else:
                err = PSReturn(None, PSFlag.HTTPERROR, 1)
            print(f'HTTP {data.status_code} {err._errcount}/{ERRLIMIT}')
            sleep(5)
            continue

        posts: Dict = {s['id']: s for s in data.json()['data']}
        if with_comments:
            subm = [
                Submission(posts[k], query_submission_comments(k))
                for k in posts.keys()
            ]
        else:
            subm = [Submission(posts[k]) for k in posts.keys()]

        if len(subm) == 0:
            if err and err.flag == PSFlag.SUBMLENERROR:
                if err._errcount == ERRLIMIT:
                    raise ValueError(
                        f'Empty subm: {submissions[-1].created_utc}'
                    )
                err._errcount += 1
            else:
                err = PSReturn(None, PSFlag.SUBMLENERROR, 1)
            sleep(1)
            continue

        submissions = sorted(subm, key=lambda s: s.created_utc)
        # print(f'#submissions: {len(submissions)} (subm: {len(subm)})')
        # print(f'last: {datetime.fromtimestamp(submissions[-1].created_utc)}')

        nsubs = len(submissions)
        if submissions[-1].created_utc >= before or nsubs == 0:
            for sub in submissions:
                yield sub
            print(
                f'({prev_time.strftime("%Y-%m-%dT%H:%M:%S%Z")}) Finished batch of {nsubs} in {str(datetime.now() - prev_time)}.\n'
            )
            break
            # return submissions, PSReturn(submissions[-1].created_utc, PSFlag.DONE)
        else:
            new_after = f'after={submissions[-1].created_utc}'
            for sub in submissions:
                yield sub

            print(
                f'({datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z")}) Finished batch of {nsubs} in {str(datetime.now() - prev_time)} (last {new_after}).\n'
            )
            prev_time = datetime.now()
            param_str = re.sub(
                r'([&?])after=.*([&$])', f'\g<1>{new_after}\g<2>', param_str
            )
