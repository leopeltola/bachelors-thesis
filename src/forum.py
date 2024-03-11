import asyncio
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import aiohttp


from src.fetcher import fetch_all


class Website:
    """Represents a website with forums, threads, and posts."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.forums: list[Forum] = []
        self.threads: list[Thread] = []
        self.posts: list[Post] = []

    def load_and_save_forum(self, label: str, id: int) -> None:
        if " " in label:
            raise ValueError("Label cannot contain spaces")
        website = self
        start = datetime.now()
        try:
            asyncio.run(website.load_forum(label, id))
        except Exception as e:
            # dump saved stuff to disk
            print("Error loading forum: ", e)
            website.threads_as_dataframe().to_csv(f"{id}_threads.csv")
            website.posts_as_dataframe().to_csv(f"{id}_posts.csv")
            return
        print(
            "\nLoading forum {} took {} seconds".format(
                label, (datetime.now() - start).seconds
            )
        )
        threads = website.threads_as_dataframe()
        print(threads)
        posts = website.posts_as_dataframe()
        print(posts)
        threads.to_csv(f"{id}_threads.csv")
        posts.to_csv(f"{id}_posts.csv")

    async def load_forum(self, label: str, id: int) -> None:
        """Add a forum to the website."""
        urls = [self.url + f"/forums/{label}.{id}?order=post_date&direction=asc"]
        print(f"Loading forum {label}.{id}...")
        pages_html: list[str] = []
        async with aiohttp.ClientSession() as session:
            htmls = await fetch_all(session, urls)
            for html in htmls:
                pages_html.append(html)

        # Parse the html to get the number of pages
        soup = BeautifulSoup(pages_html[0], "html.parser")
        nav = soup.find_all("ul", {"class": "pageNav-main"})[0]
        pages_cont = int(nav.find_all("li")[-1].a.text)  # type: ignore

        # fetch all the forum pages
        urls = [
            self.url + f"/forums/{label}.{id}/page-{i}?order=post_date&direction=asc"
            for i in range(2, pages_cont + 1)
        ]
        print(f"Fetching {len(urls)} pages...")
        async with aiohttp.ClientSession() as session:
            htmls = await fetch_all(session, urls)
            for html in htmls:
                pages_html.append(html)

        # Parse the html to get the threads
        print(f"Parsing {len(pages_html)} pages...")
        for i, html in enumerate(pages_html):
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
                author: str = thread.get("data-author")
                self.threads.append(Thread(url_label, id, link.text, author, pages))
            print(f"Parsed page {i + 1}/{len(pages_html)}...")

        print("Threads:", len(self.threads))

        # Get thread pages
        urls: list[str] = []
        for thread in self.threads:
            urls.append(
                self.url
                + f"/threads/{thread.url_label}.{thread.id}/?order=post_date&direction=asc"
            )
            if thread.pages > 1:
                for i in range(2, thread.pages + 1):
                    urls.append(
                        self.url
                        + f"/threads/{thread.url_label}.{thread.id}/page-{i}?order=post_date&direction=asc"
                    )

        print(f"Fetching {len(urls)} thread pages...")
        thread_html: list[str] = []
        async with aiohttp.ClientSession() as session:
            thread_html += await fetch_all(session, urls)

        # Parse the html to get the posts
        print(f"Parsing {len(thread_html)} thread pages...")
        for i, html in enumerate(thread_html):
            soup = BeautifulSoup(html, "html.parser")
            thread_id_src = soup.find_all(
                "div", class_="block-container lbContainer", recursive=True
            )[0].get("data-lb-id")
            thread_id: int = int(thread_id_src.split("-")[-1])
            print("Thread id:", thread_id)

            # TODO: Get the posts from html
            first = soup.select(
                "article.message.message--article.js-post.js-inlineModContainer.is-first",
            )
            if first:
                # First post
                post = first[0]
                author = post.get("data-author")  # type: ignore
                post_id = int(post.get("data-content").split("-")[-1])  # type: ignore
                inner_bb = post.select("div.bbWrapper")[0]
                content = inner_bb.text
                time_posted = datetime.fromisoformat(
                    post.select("time")[0].get("datetime")  # type: ignore
                )
                self.posts.append(
                    Post(author, post_id, content, thread_id, time_posted)
                )
            articles_cont = soup.select("div.block-body.js-replyNewMessageContainer")
            if not articles_cont:
                print(f"No articles found in thread {thread_id}")
            else:
                articles = articles_cont[0].select(
                    "article.message.message--post.js-post.js-inlineModContainer"
                )
                for article in articles:
                    author = article.get("data-author")  # type: ignore
                    post_id = int(article.get("data-content").split("-")[-1])  # type: ignore
                    content = article.select("div.bbWrapper")[0].text
                    time_posted = datetime.fromisoformat(
                        article.select("time.u-dt")[0].get("datetime")  # type: ignore
                    )
                    self.posts.append(
                        Post(author, post_id, content, thread_id, time_posted)
                    )

    def threads_as_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.threads)
        df.set_index("id", drop=True, inplace=True)  # type: ignore
        return df

    def posts_as_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.posts)
        df.set_index("id", drop=True, inplace=True)  # type: ignore
        return df


@dataclass
class Thread:
    """Represents a thread in a forum"""

    url_label: str
    id: int
    title: str
    author: str
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
    date_posted: datetime
    """The date the post was made"""
