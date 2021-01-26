from stigmapyze.scraping import reddit


if __name__ == '__main__':
    rconn = reddit.connect_and_configure('config.json')
    posts = reddit.parse_subreddit(10, rconn, 'SuicideWatch')

    with open('data/output/posts.json', 'w') as f:
        for post in posts:
            print(post)
            # post.write_post(f)
