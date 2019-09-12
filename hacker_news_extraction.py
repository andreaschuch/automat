import requests
from collections import Counter
from collections import namedtuple
import multiprocessing as mp
import argparse


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

    def __init__(self, number_of_topstories, number_of_commenters):
        """
        Construct a HackerNewsExtractor
        :param number_of_topstories: The number of topstories to be considered. (int)
        :param number_of_commenters: The number of commenters to be considered. (int)
        """
        self.number_of_topstories = number_of_topstories
        self.number_of_commenters = number_of_commenters
        self.comments = {}
        self.comments["total"] = Counter()
        self.titles = {}

    def run(self):
        """
        Extracts the following information from Hacker News API:
        For each of the top 30 stories, we want to have an output containing:
         - The story title
         - The top 10 commenters of that story.
        For each commenter:
        - The number of comments they made on the story.
        - The total number of comments they made among all the top 30 stories.
        :return: List of namedtuples with the following fields: "id", "title", "users".
        The later is a namedtuple with the following fields: "name", "number_of_comments", "total_number_of_comments"
        """
        top_stories = self._retrieve_top_story_ids()
        pool = mp.Pool(mp.cpu_count())
        extracted_stories = pool.map(func=self._retrieve_story_information, iterable=top_stories)
        pool.close()
        pool.join()
        for story_id, title, author_counter in extracted_stories:
            self.titles[story_id] = title
            self.comments['total'].update(author_counter)
            self.comments[story_id] = author_counter
        results = self._extract_information(top_stories)
        return results

    def print_result(self, stories):
        """
        Prints the extracted information in the required format.
        :param stories: The stories to be printed. (namedtuple("Result", ["id", "title", "users"] with "users" being a namedtuple("User", ["name", "number_of_comments", "total_number_of_comments"]))
        :return: None
        """
        for story in stories:
            string_to_print = "| "
            string_to_print += story.title
            string_to_print += " | "
            for user in story.users:
                string_to_print += user.name+" (" +str(user.number_of_comments)+ " for story - "+str(user.total_number_of_comments)+ " total) | "
            print(string_to_print)

    def _retrieve_top_story_ids(self):
        """
        Retrieves the ids of the Hacker News top stories.
        The number of top stories has been specified by the number_of_topstories parameter in the constructor.
        :return: List of ids (List of str).
        """
        top_stories = requests.get(self.top_story_url).json()
        return top_stories[0:self.number_of_topstories]

    def _retrieve_comment_counts(self, item_ids, acc=None):
        """
        Recursive method to the number of comments from each user.
        :param item_ids: List of item ids to be considered (List of str)
        :param acc: The accumulator parameter used during the recursion. (Do not specify.)
        :return: A counter of the user names (Counter { username -> number_of_comments} )
        """
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
                    acc.update(self._retrieve_comment_counts(item_ids=kid_ids, acc=None))
        return acc

    def _extract_information(self, top_stories):
        """
        Extracts the following information from the internal storage (self.comments and self.titles):
        - id and title of each story
        - top commenters as well their number of comments on the particular story and in total
        :param top_stories: Ids of the top stories. (List of int)
        :return: List of Namedtuples with the following fields: "id", "title", "users".
        The later is a namedtuple with the following fields: "name", "number_of_comments", "total_number_of_comments"
        """
        results = []
        Result = namedtuple("Result", ["id", "title", "users"])
        for story_id in top_stories:
            users = []
            if not self.comments[story_id]:
                print ("Story without comments: "+str(story_id))
            for comment in self.comments[story_id].most_common(n=self.number_of_commenters):
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

    def _retrieve_story_information(self, story_id):
        """
        Retrieves the story title and number of comments per user from the Hacker News API.
        :param story_id: The Id specifying the story.
        :return: A namedtuple with the following fields: "story_id", "title", "comment_counter". The latter contains a comment counter for all users.
        """
        story_item = requests.get("https://hacker-news.firebaseio.com/v0/item/" + str(story_id) + ".json").json()

        title = story_item["title"]
        try:
            kid_ids = story_item['kids']
        except KeyError:
            kid_ids = []
        User = namedtuple("User", ["story_id", "title", "comment_counter"])
        return story_id, title, self._retrieve_comment_counts(item_ids=kid_ids)



if __name__ == "__main__":
    parser = argparse.ArgumentParser( formatter_class=argparse.RawTextHelpFormatter,
    description="This program extracts the following information from the Hacker News API (https://github.com/HackerNews/API):" "\n"
    "The title of the 30 top stories and the names of the most frequent commmentators. " "\n"
    "For instance, if we consider just the 3 top stories (instead of 30) and top 2 commenters (instead of 10):" "\n"
        "| Story A | Story B | Story C |" "\n"
        " |--------------------|---------------------|---------------------|" "\n"
        " | user-a (1 comment) | user-a (4 comments) | user-a (4 comments) |" "\n"
        " | user-b (2 comment) | user-b (3 comments) | user-b (5 comments) |""\n"
        " | user-c (3 comment) | user-c (2 comments) | user-c (3 comments) |""\n"
        " We get the output to look as follows:""\n"
        " | Story | 1st Top Commenter | 2nd Top Commenter |""\n"
        " |---------|---------------------------------|---------------------------------|""\n"
        " | Story A | user-c (3 for story - 8 total) | user-b (2 for story - 10 total) |""\n"
                                                 "")
    parser.add_argument("--number_of_topstories", type=int, default=30, help="Specifies the number of top stories to be considered. (Default is 30.)")
    parser.add_argument("--number_of_commenters", type=int, default=10,  help="Specifies the number of top commenter to be considered. (Default is 10.)")
    args = parser.parse_args()
    extractor = HackerNewsExtractor(number_of_topstories=args.number_of_topstories,
                                    number_of_commenters=args.number_of_commenters)
    stories = extractor.run()
    extractor.print_result(stories)