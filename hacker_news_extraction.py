import requests
from collections import Counter
from collections import namedtuple
import multiprocessing as mp


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

    top_story_url ="https://hacker-news.firebaseio.com/v0/topstories.json"

    def __init__(self):
        self.comments = {}
        self.comments["total"] = Counter()
        self.titles = {}

    def extract_top_stories(self, number_of_topstories):
        top_stories = requests.get(self.top_story_url).json()
        return top_stories[0:number_of_topstories]

    def extract_comment_counts(self, item_ids, acc=None):
        if acc is None:
            acc = Counter()
        for item_id in item_ids:
            item = requests.get("https://hacker-news.firebaseio.com/v0/item/"+str(item_id)+".json").json()
            if not item:
                print("Could not access: "+ str(item_id))
            else:
                if item["type"]=="comment" and "by" in item:
                    author = item['by']
                    acc.update([author])
                if 'kids' in item:
                    kid_ids = item['kids']
                    acc.update(self.extract_comment_counts(item_ids=kid_ids, acc=None))
        return acc

    def extract(self, number_of_topstories, number_of_commenters):
        Result = namedtuple("Result", ["id", "title", "users"])

        top_stories = self.extract_top_stories(number_of_topstories)
        pool = mp.Pool(mp.cpu_count())
        extracted_stories = pool.map(func=self.extract_story, iterable=top_stories)

        for story_id, title, author_counter in extracted_stories:
            self.titles[story_id] = title
            self.comments['total'].update(author_counter)
            self.comments[story_id] = author_counter

        results = []
        for story_id in top_stories:
            users = []
            if not self.comments[story_id]:
                print ("Story without comments: "+str(story_id))
            for comment in self.comments[story_id].most_common(n=number_of_commenters):
                user_name = comment[0]
                User = namedtuple("User", ["name", "number_of_comments", "total_number_of_comments"])
                number_of_comments = self.comments[story_id][user_name]
                total_number_of_comments = self.comments['total'][user_name]
                user = (User(name=user_name, number_of_comments=number_of_comments,
                             total_number_of_comments=total_number_of_comments))
                users.append(user)
            result = Result(id=story_id, title=self.titles[story_id], users=users)
            results.append(result)

        return results

    def extract_story(self, story_id):
        story_item = requests.get("https://hacker-news.firebaseio.com/v0/item/" + str(story_id) + ".json").json()

        title = story_item["title"]
        try:
            kid_ids = story_item['kids']
        except KeyError:
            kid_ids = []

        return story_id, title, self.extract_comment_counts(item_ids=kid_ids)

    def print_result(self, stories):
        for story in stories:
            string_to_print = "| "
            string_to_print += story.title
            string_to_print += " | "
            for user in story.users:
                string_to_print += user.name+" (" +str(user.number_of_comments)+ " for story - "+str(user.total_number_of_comments)+ " total) | "
            print(string_to_print)


if __name__ == "__main__":
    extractor = HackerNewsExtractor()
    stories = extractor.extract(number_of_topstories=30, number_of_commenters=10)
    extractor.print_result(stories)