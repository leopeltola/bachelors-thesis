from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp


from fetcher import fetch_all


class Website:
    """Represents a website with forums, threads, and posts."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.forums: list[Forum] = []
        self.threads: list[Thread] = []
        self.posts: list[Post] = []

    def load_thread(self, url_label: str, id: int) -> None:
        """Load a thread and its posts from the website."""
        pass

    async def load_forum(self, label: str, id: int) -> None:
        """Add a forum to the website."""
        urls = [self.url + f"/forums/{label}.{id}?order=post_date&direction=asc"]
        pages_html: list[str] = []
        async with aiohttp.ClientSession() as session:
            htmls = await fetch_all(session, urls)
            for html in htmls:
                pages_html.append(html)

        # Parse the html to get the number of pages
        soup = BeautifulSoup(pages_html[0], "html.parser")
        nav = soup.find_all("ul", {"class": "pageNav-main"})[0]
        pages_cont = int(nav.find_all("li")[-1].a.text)  # type: ignore

        # fetch all the pages
        urls = [
            self.url + f"/forums/{label}.{id}/page-{i}?order=post_date&direction=asc"
            for i in range(2, pages_cont + 1)
        ]
        async with aiohttp.ClientSession() as session:
            htmls = await fetch_all(session, urls)
            for html in htmls:
                pages_html.append(html)

        # Parse the html to get the threads
        for _i, html in enumerate(pages_html):
            soup = BeautifulSoup(html, "html.parser")
            thread_list = soup.find_all(
                "div",
                {"class": "js-threadList"},
                recursive=True,
            )[0]
            threads = thread_list.find_all("div", recursive=False)
            for thread in threads:
                link = thread.find_all("a", {"data-tp-primary": "on"}, recursive=True)[
                    0
                ]
                pages_cont = thread.find(
                    "span", class_="structItem-pageJump", recursive=True
                )
                pages: int = 1
                if pages_cont:
                    pages = int(pages_cont.find_all("a", recursive=False)[-1].text)
                href = link.get("href")
                temp = href.split("/")[-2]
                temp = temp.split(".")
                id = int(temp[-1])
                url_label = "".join(temp[:-1])
                self.threads.append(Thread(url_label, id, link.text, pages))


@dataclass
class Thread:
    """Represents a thread in a forum"""

    url_label: str
    id: int
    title: str
    pages: int
    """The number of pages in the thread"""


@dataclass
class Forum:
    """Represents a forum on a website"""

    url_label: str
    id: int
    title: str
    pages: int
    """The number of pages in the forum"""


@dataclass
class Post:
    """Represents a post in a forum thread"""

    author: str
    """The author of the post"""
    id: int
    """The id of the post"""
    content: str
    """The content of the post"""
    thread_id: int
    """The id of the thread to which this post belongs"""
    nth_post_by_author: int = -1
    """The nth post by the author. -1=unknown"""
    date_posted: datetime = datetime.now()
    """The date the post was made"""
