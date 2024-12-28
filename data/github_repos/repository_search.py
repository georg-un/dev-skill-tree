import math

from github import Github


class RepositorySearch:
    max_allowed_stars = 500_000 # largest repo on GitHub is currently at 430_000 stars
    current_max_stars = max_allowed_stars
    default_increment = 100
    results_buffer = []

    def __init__(self, github_token: str, min_stars: int, language: str):
        """
        GitHub only supports up to 1000 results per search query (see https://github.com/PyGithub/PyGithub/issues/1309#issuecomment-871000409).
        Therefore, we potentially have to slice our search query into multiple smaller queries.
        This class is basically a generator encapsulating the slicing logic.

        You can call it as follows:
        ```
        search = RepositorySearch(github_token, 50_000, "JavaScript")
        for repo in search.query():
            do_stuff(repo)
        ```

        :param github_token: GitHub API token
        :param min_stars: Minimum number of stars for a repo
        :param language: Language of the repo
        """
        self.github = Github(github_token)
        self.current_min_stars = min_stars
        self.language = language

    def _are_results_buffered(self):
        return len(self.results_buffer) > 0

    def _increment_stars_slice(self):
        self.current_min_stars = self.current_max_stars + 1
        self.current_max_stars = self.current_max_stars + self.default_increment

    def _query_next_batch(self):
        if self.current_min_stars > self.max_allowed_stars:
            return []

        query = f"stars:{self.current_min_stars}..{self.current_max_stars} language:{self.language}"
        result = self.github.search_repositories(query)

        # Happy path:
        if 0 < result.totalCount < 1000:
            self._increment_stars_slice()
            return [repo for repo in result]
        # More results than
        if result.totalCount >= 1000:
            self.current_max_stars = self.current_min_stars + math.floor((self.current_max_stars - self.current_min_stars) / 2)
            return self._query_next_batch()
        if result.totalCount == 0:
            self._increment_stars_slice()
            return self._query_next_batch()

    def query(self):
        """
        Generator function to search for repositories by slicing the search query into star ranges.
        """
        if self._are_results_buffered():
            yield self.results_buffer.pop()
        else:
            self.results_buffer = self._query_next_batch()
            if self._are_results_buffered():
                yield self.results_buffer.pop()
