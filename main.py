import json
from stigmapyze.scraping import reddit


if __name__ == '__main__':
    rconn = reddit.connect_and_configure('config.json')
    posts = reddit.parse_subreddit(2, rconn, 'SuicideWatch')

    with open('data/output/posts.json', 'w', encoding='utf-8') as f:
        f.write('[\n')
        for post in posts:
            post.write_post(f)
            f.write(',\n')
        f.write('\n]')
        # json.dump(list(map(lambda x: x.__dict__, posts)), f, indent=4, ensure_ascii=False)
        # post.write_post(f)
