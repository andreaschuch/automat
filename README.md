# Description
This program downloads stories from the Hacker News API: https://github.com/HackerNews/API
For each of the top 30 stories, we want to have an output containing:
 - The story title
 - The top 10 commenters of that story.
For each commenter:
- The number of comments they made on the story.
- The total number of comments they made among all the top 30 stories.
# Pre-requisites:
Requires python 3.x

# Running instructions:
python hacker_news_extraction.py

For more information run

python hacker_news_extraction.py --help

# Run the unittests:
python test_hacker_news_extraction.py

