import unittest
from hacker_news_extraction import HackerNewsExtractor


class TestHackerNewsExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = HackerNewsExtractor()

    def test_extract_topstories(self):
        number_of_topstories = 10
        top_stories = self.extractor.extract_top_stories(number_of_topstories)
        self.assertEqual(number_of_topstories, len(top_stories))

    def test_extract_comments(self):
        result = self.extractor.extract_comment_counts(item_ids=self.extractor.extract_top_stories(3))
        assert result

    def test_extract_example(self):
    # For instance, if we consider just the 3 top stories (instead of 30) and top 2 commenters (instead of 10):
        number_of_topstories=3
        number_of_commenters=2
        stories = self.extractor.extract(number_of_topstories=number_of_topstories, number_of_commenters=number_of_commenters)
        # | Story A | Story B | Story C |
        # |--------------------|---------------------|---------------------|
        # | user-a (1 comment) | user-a (4 comments) | user-a (4 comments) |
        # | user-b (2 comment) | user-b (3 comments) | user-b (5 comments) |
        # | user-c (3 comment) | user-c (2 comments) | user-c (3 comments) |
        # We want the output to look as follows:
        # | Story | 1st Top Commenter | 2nd Top Commenter |
        # |---------|---------------------------------|---------------------------------|
        # | Story A | user-c (3 for story - 8 total) | user-b (2 for story - 10 total) |

        self.assertEqual(number_of_topstories, len(stories))
        for story in stories:
            assert(story.title)
            assert(story.users)
            self.assertGreaterEqual(number_of_commenters, len(story.users))
            for user in story.users:
                assert(user.name)
                assert(user.number_of_comments)
                assert(user.total_number_of_comments)
        self.extractor.print_result(stories)

if __name__=="__main__":
    unittest.main()

