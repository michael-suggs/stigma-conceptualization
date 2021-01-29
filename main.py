from datetime import timedelta
from praw.models import Submission
from stigmapyze.scraping import reddit


if __name__ == '__main__':
    timelimit = timedelta(weeks=1)
    rconn = reddit.connect_and_configure('config.json')
    posts = reddit.parse_subreddit(timelimit, rconn, 'SuicideWatch')

    with open('data/output/posts.json', 'w', encoding='utf-8') as f:
        f.write('[\n')
        posts.__next__().write_post(f)
        for post in posts:
            f.write(',\n')
            post.write_post(f)
        f.write('\n]')
