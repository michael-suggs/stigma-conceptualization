from copy import deepcopy
from datetime import datetime
import json
from typing import Iterator, List, Optional, Union


class RedditContent:

    def __init__(self, resp: dict) -> None:
        self.author = resp.get('author')
        self.created_utc = resp.get('created_utc')
        self.id = resp.get('id')
        self.score = resp.get('score')

    def __eq__(self, o: object) -> bool:
        return self.created_utc == o.created_utc

    def __lt__(self, o: object) -> bool:
        return self.created_utc < o.created_utc

    def __gt__(self, o: object) -> bool:
        return self.created_utc > o.created_utc

    def __str__(self) -> str:
        return json.dumps(vars(self), indent=4)

    @staticmethod
    def csv_fields() -> List[str]:
        return ['created_utc', 'id', 'score', 'author']


class Comment(RedditContent):

    def __init__(self, resp: dict) -> None:
        super().__init__(resp)
        self.body = resp.get('body')
        self.is_submitter = resp.get('is_submitter')
        self.link_id = resp.get('link_id')
        self.parent_id = resp.get('parent_id').split('_')[-1]

    def params(self, datefmt: str = None) -> dict:
        v = vars(self)
        if datefmt:
            try:
                v['created_utc'] = datetime.fromtimestamp(v['created_utc']).strftime(datefmt)
            except:
                print(f'Could not format {v["created_utc"]} with format string {datefmt}.')
        return v

    @staticmethod
    def csv_fields() -> List[str]:
        return [
            'created_utc',
            'id',
            'score',
            'author',
            'is_submitter',
            'parent_id',
            'link_id',
            'body',
        ]

    @classmethod
    def csv_header(cls) -> str:
        return ','.join(cls.csv_fields())



class Submission(RedditContent):

    def __init__(
        self,
        resp: dict,
        comments: Optional[Union[dict, List[Comment]]] = None
    ) -> None:
        super().__init__(resp)

        if isinstance(comments, dict):
            self.comments = [Comment(c) for c in comments]
        elif isinstance(comments, list):
            if all(map(lambda e: isinstance(e, Comment), comments)):
                self.comments = comments
            else:
                for i in range(len(comments)):
                    if not isinstance(comments[i], Comment):
                        comments[i] = Comment(comments[i])
                self.comments = comments
        else:
            self.comments = None

        self.full_link = resp.get('full_link')
        self.selftext = resp.get('selftext')
        self.title = resp.get('title')

    def params(self, csv: bool = False, datefmt: str = None) -> dict:
        v = deepcopy(vars(self))
        # print(v)
        comment_ids = list(map(lambda c: c.id, v['comments'])) if v['comments'] else []
        v['comments'] = comment_ids if not csv else str(comment_ids)
        if datefmt:
            try:
                v['created_utc'] = datetime.fromtimestamp(v['created_utc']).strftime(datefmt)
            except:
                print(f'Could not format {v["created_utc"]} with format string {datefmt}.')
        return v

    def get_comments(self) -> List[Comment]:
        return self.comments

    @staticmethod
    def csv_fields() -> List[str]:
        return [
            'created_utc',
            'id',
            'score',
            'author',
            'title',
            'full_link',
            'comments',
            'selftext',
        ]

    @classmethod
    def csv_header(cls) -> str:
        return ','.join(cls.csv_fields())
