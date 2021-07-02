# Stigma Conceptualization

## Layout

### `stigmapyze`

The main project file containing the majority of all relevant code is the [`stigmapyze`](stigmapyze) package, which is broken down into a number of submodules. [`common`](stigmapyze/common/reddit.py) contains both Submission and Comment data structures used to hold relevant Reddit data when scraped via PushShift (the primary source of data scraping), and the [`reddit_post`](stigmapyze/common/reddit_post.py) module contains data structures for managing content obtained from PRAW (which sadly provides less efficacy in this use case due to its limited scraping ability)

The [`scraping`](stigmapyze/scraping/) package contains multiple files for scraping Reddit posts, with the main methods used for the obtained data being present in [`pushshift.py`](stigmapyze/scraping/pushshift.py). [`util.py`](stigmapyze/scraping/util.py) contains methods for scraping content until all posts in a given range are obtained, which is necessary due to both PushShift and PRAW's limitation on the amount of posts/comments returned in a single request.

### Jupyter Notebooks

[`fix_comments`](notebooks/fix_comments.ipynb)--used to fix some errors that were present in the original scraping methods that resulted in comments being returned that were not actual comments on the desired post, but of posts from different subreddits that happened to share the same post ID.

[`data_manipulation`](notebooks/data_manipulation.ipynb)--used after tagging to drop posts left untagged or with non-binary results in their columns, keeping only data that was deemed taggable. A vast number of both posts and comments either did not contain enough information to be tagged or were simply uncategorizable with the given cues, and were thusly removed.

[`analysis`](notebooks/analysis.ipynb)--this contains the final setup of the data in preparation for learning, followed by a number of models used to classify the given texts. Models are split on three methods of data preprocessing; a count vectorizer, keras' sequence tokenizer, and lastly using TF-IDF.
