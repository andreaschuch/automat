import requests
from collections import Counter
from collections import namedtuple


class HackerNewsExtractor:
    """
    This program downloads stories from the Hacker News API: https://github.com/HackerNews/API
    For each of the top 30 stories, we want to have an output containing:
     - The story title
     - The top 10 commenters of that story.
    For each commenter:
    - The number of comments they made on the story.
    - The total number of comments they made among all the top 30 stories.
    """

    # TODO We need the program to parallelize the requests and aggregate the results as efficiently as possible. This is one of the main aspects that our recruiting team will pay attention to when assessing your solution.

    top_story_url ="https://hacker-news.firebaseio.com/v0/topstories.json"

    def __init__(self):
        self.comments = {}
        self.comments["total"] = Counter()
        self.titles = {}

    def extract_top_stories(self, number_of_topstories):
        top_stories = requests.get(self.top_story_url).json()
        return top_stories[0:number_of_topstories]

    def extract_comments(self, story_id, ids):
        for id in ids:
            item = requests.get("https://hacker-news.firebaseio.com/v0/item/"+str(id)+".json").json()
            if item["type"]=="comment" and "by" in item:
                author = item['by']
                self.comments["total"].update([author])
                try:
                    counter_per_story = self.comments[story_id]
                except KeyError:
                    counter_per_story = Counter()
                    self.comments[story_id] = counter_per_story
                counter_per_story.update([author])
            try:
                kid_ids = item['kids']
            except KeyError:
                return

            return self.extract_comments(story_id=story_id, ids=kid_ids)

    def extract(self, number_of_topstories, number_of_commenters):
        Result = namedtuple("Result", ["id", "title", "users"])

        top_stories = self.extract_top_stories(number_of_topstories)
        for story in top_stories:
            story_item = requests.get("https://hacker-news.firebaseio.com/v0/item/" + str(story) + ".json").json()

            self.titles[story] = story_item["title"]
            try:
                kid_ids = story_item['kids']
            except KeyError:
                kid_ids = []
            self.comments[story] = Counter()
            self.extract_comments(story_id=story, ids=kid_ids)

        results = []
        for story in top_stories:
            users = []
            for comment in self.comments[story].most_common(n=number_of_commenters):
                user_name = comment[0]
                User = namedtuple("User", ["name", "number_of_comments", "total_number_of_comments"])
                number_of_comments = self.comments[story][user_name]
                total_number_of_comments = self.comments['total'][user_name]
                user = (User(name=user_name, number_of_comments=number_of_comments, total_number_of_comments=total_number_of_comments))
                users.append(user)
            result = Result(id=story, title=self.titles[story], users=users)
            results.append(result)

        return results


