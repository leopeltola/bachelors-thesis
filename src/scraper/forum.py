import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
import aiohttp


from src.scraper.fetcher import fetch_all
from src.utils import print_progress_bar


class Website:
    """
    Represents a website to be scraped. Actual analysis is done in the analyze.py file using DataFrames.

    Attributes:
        url (str): The URL of the website.
        forums (list[Forum]): A list of forums on the website.
        threads (list[Thread]): A list of threads on the website.
        posts (list[Post]): A list of posts on the website.
    
    """
    def __init__(self, url: str) -> None:
        self.url = url
        self.forums: list[Forum] = []
        self.threads: list[Thread] = []
        self.posts: list[Post] = []

    def load_and_save_forum(self, label: str, id: int) -> None:
        """
        Loads and saves a forum with the given label and ID.

        Args:
            label (str): The label of the forum.
            id (int): The ID of the forum.

        Raises:
            ValueError: If the label contains spaces.

        Returns:
            None
        """
        if " " in label:
            raise ValueError("Label cannot contain spaces")
        path: Path = Path(f"data/")
        save_label: str = f"{label}_{datetime.now().strftime(r"%Y-%m-%d_%H.%M.%S")}"

        start = datetime.now()
        try:
            asyncio.run(self.load_forum(label, id))
        except Exception as e:
            # dump saved stuff to disk
            print("Error loading forum: ", e)
            self.threads_as_dataframe().to_csv(
                path / f"ERROR_threads_{save_label}.csv"
            )
            self.posts_as_dataframe().to_csv(
                path / f"ERROR_posts_{save_label}.csv"
            )
            return
        print(
            "\nLoading forum {} took {} seconds".format(
                label, (datetime.now() - start).seconds
            )
        )
        threads = self.threads_as_dataframe()
        print(threads)
        posts = self.posts_as_dataframe()
        print(posts)
        threads.to_csv(path / f"threads_{save_label}.csv")
        posts.to_csv(path / f"posts_{save_label}.csv")

    async def load_forum(self, label: str, id: int) -> None:
            """
            Loads a forum with the specified label and ID.

            Args:
                label (str): The label of the forum.
                id (int): The ID of the forum.

            Returns:
                None
            """
            print(f"Loading forum {label}.{id}...")
            
            urls = [self.url + f"/forums/{label}.{id}?order=post_date&direction=asc"]
            pages_html: list[str] = []
            async with aiohttp.ClientSession() as session:
                pages_html += await fetch_all(session, urls)

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
                pages_html = await fetch_all(session, urls)

            # Parse the html to get the threads
            _threads = self.extract_threads_from_html(pages_html)

            self.threads += _threads # Add to total threads
            print("Threads:", len(self.threads))

            # Get thread paged urls
            urls = self.generate_thread_urls(_threads)

            print(f"Fetching {len(urls)} thread pages...")
            thread_html: list[str] = []
            async with aiohttp.ClientSession() as session:
                thread_html += await fetch_all(session, urls)

            # Parse the html to get the posts
            print(f"Parsing {len(thread_html)} thread pages...")
            _posts = self.extract_posts_from_html(thread_html)
            self.posts += _posts

    def extract_posts_from_html(self, thread_html: list[str]):
        """
        Extracts posts from HTML and returns a list of Post objects.

        Args:
            thread_html (list[str]): A list of HTML strings representing the threads.

        Returns:
            list[Post]: A list of Post objects extracted from the HTML.

        """
        _posts: list[Post] = []
        for i, html in enumerate(thread_html):
            soup = BeautifulSoup(html, "html.parser")
            thread_id_src = soup.find_all(
                "div", class_="block-container lbContainer", recursive=True
            )[0].get("data-lb-id")
            thread_id: int = int(thread_id_src.split("-")[-1])
            print_progress_bar(
                i + 1, len(thread_html), prefix="Processing threads:", suffix="complete"
            )

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
                for quote in inner_bb.find_all("blockquote"):
                    quote.decompose() # Remove quotes. TODO: images and videos
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
                    author: str = article.get("data-author")  # type: ignore
                    post_id = int(article.get("data-content").split("-")[-1])  # type: ignore
                    inner_bb = article.select("div.bbWrapper")[0]
                    for quote in inner_bb.find_all("blockquote"):
                        quote.decompose()
                    content = inner_bb.text
                    time_posted = datetime.fromisoformat(
                        article.select("time.u-dt")[0].get("datetime")  # type: ignore
                    )
                    _posts.append(
                        Post(author, post_id, content, thread_id, time_posted)
                    )
                    
        return _posts

    def generate_thread_urls(self, threads: list["Thread"]):
        """
        Generates a list of URLs for the given threads.

        Args:
            threads (list[Thread]): A list of Thread objects.
        
        Returns:
            list[str]: A list of URLs for the given threads.
        """
        urls: list[str] = []
        for thread in threads:
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
                    
        return urls

    def extract_threads_from_html(self, pages_html: list[str]):
        """
        Extracts threads from HTML pages.

        Args:
            pages_html (list[str]): A list of HTML pages.

        Returns:
            list[Thread]: A list of Thread objects extracted from the HTML pages.
        """
        print(f"Parsing {len(pages_html)} pages...")
        _threads: list[Thread] = []
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
                _threads.append(Thread(url_label, id, link.text, author, pages))
            print(f"Parsed page {i + 1}/{len(pages_html)}...")
        return _threads



    def threads_as_dataframe(self) -> pd.DataFrame:
            """
            Converts the threads data into a pandas DataFrame.

            Returns:
                pd.DataFrame: A DataFrame containing the threads data.
            """
            df = pd.DataFrame(self.threads)
            df.set_index("id", drop=True, inplace=True)  # type: ignore
            return df

    def posts_as_dataframe(self) -> pd.DataFrame:
            """
            Converts the posts data into a pandas DataFrame.

            Returns:
                pd.DataFrame: A DataFrame containing the posts data.
            """
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
    scraped: datetime = datetime.now()
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

