from csv import DictWriter
from datetime import datetime, timedelta
from typing import Final, List, Literal

import pandas as pd

from .pushshift import query_submissions
from ..common.reddit import Comment, Submission

DATE_FORMAT: Final[str] = '%Y-%m-%dT%H:%M:%S%Z'
STIGMA_HEADER: Final[List[str]] = [
    'ID',
    'Stig_c1',
    'Stig_c2',
    'Stig_c3',
    'Stig_c4',
    'Stig_c5',
    'Challn_c1',
    'Challn_c2',
    'Challn_c3',
    'Challn_c4',
    'Challn_c5'
]


def stigma_row(id: str, type: Literal['Submission', 'Comment']) -> dict:
    row = {col: '' for col in STIGMA_HEADER}
    row['ID'] = f'{type} {id}'
    return row


def scrape_until():
    now = datetime.utcnow()
    after_date = (now - timedelta(days=30))

    try:
        sub_file = open(
            f'data/input/{after_date.strftime(DATE_FORMAT)}-{now.strftime(DATE_FORMAT)}-submissions.csv',
            'w'
        )
        sub_csv = DictWriter(sub_file, fieldnames=Submission.csv_fields())
        sub_csv.writeheader()

        cmt_file = open(
            f'data/input/{after_date.strftime(DATE_FORMAT)}-{now.strftime(DATE_FORMAT)}-comments.csv',
            'w'
        )
        cmt_csv = DictWriter(cmt_file, fieldnames=Comment.csv_fields())
        cmt_csv.writeheader()

        stg_file = open(
            f'data/input/{after_date.strftime(DATE_FORMAT)}-{now.strftime(DATE_FORMAT)}-stigma.csv',
            'w'
        )
        stg_csv = DictWriter(stg_file, fieldnames=STIGMA_HEADER)
        stg_csv.writeheader()

        submissions = query_submissions(
            subreddit='SuicideWatch',
            after=int(after_date.timestamp()),
            size=500
        )
        scount, ccount = 0, 0
        for sub in submissions:
            sparams = sub.params(csv=True, datefmt=DATE_FORMAT)
            sub_csv.writerow(sparams)
            stg_csv.writerow(stigma_row(sparams['id'], 'Submission'))
            scount += 1
            for c in sub.get_comments():
                cparams = c.params(datefmt=DATE_FORMAT)
                cmt_csv.writerow(cparams)
                stg_csv.writerow(stigma_row(cparams['id'], 'Comment'))
                ccount += 1
            if scount % 250 == 0:
                print(f'Wrote {scount} submissions and {ccount} comments.')
        print(f'DONE. Wrote {scount} submissions and {ccount} comments.')
    finally:
        sub_file.close()
        cmt_file.close()
        stg_file.close()


def clean_csvs(sub_file: str, cmt_file: str):
    cmt = pd.read_csv(cmt_file)
    sub = pd.read_csv(sub_file)


def match_submission_comments():
    ...
