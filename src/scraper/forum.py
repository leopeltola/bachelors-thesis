import asyncio
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

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
                path / f"ERROR_threads_{save_label}.csv.zip"
            )
            self.posts_as_dataframe().to_csv(
                path / f"ERROR_posts_{save_label}.csv.zip "
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
        threads.to_csv(path / f"threads_{save_label}.csv.zip")
        posts.to_csv(path / f"posts_{save_label}.csv.zip")

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

            print(f"Fetching {len(urls)+1} pages...")
            async with aiohttp.ClientSession() as session:
                pages_html = await fetch_all(session, urls)

            # Parse the html to get the threads
            _threads = self.extract_threads_from_html(pages_html)

            self.threads += _threads # Add to total threads
            print("Threads:", len(_threads))

            # dump threads to disk
            self.threads_as_dataframe().to_csv(f"data/threads_{label}_{id}.csv.zip")
            
            # Get thread paged urls
            urls = self.generate_thread_urls(_threads)

            # Chunk the urls into batches of 10000
            urls_chunked: list[list[str]] = []
            for i in range(0, len(urls), 10000):
                urls_chunked.append(urls[i : i + 10000])
            
            for i, chunk in enumerate(urls_chunked):
                print(f"Fetching {len(chunk)} thread pages chunked {i+1}/{len(urls_chunked)}...")
                thread_html: list[str] = []
                async with aiohttp.ClientSession() as session:
                    thread_html += await fetch_all(session, chunk)

                # Parse the html to get the posts
                print(f"Parsing {len(thread_html)} thread pages in multiple threads...")
                _posts = self.extract_posts_from_html_chunk(thread_html)
                self.posts += _posts
                self.dumb_posts_to_disk()
    
    def dumb_posts_to_disk(self) -> None:
        # dump posts to disk, to the same file
        df = self.posts_as_dataframe()
        df.to_csv(f"data/posts_dump.csv.zip")

    def extract_posts_from_html_chunk(self, thread_html: list[str]):
        """
        Extracts posts from HTML and returns a list of Post objects.

        Args:
            thread_html (list[str]): A list of HTML strings representing the threads.

        Returns:
            list[Post]: A list of Post objects extracted from the HTML.

        """
        _posts: list[Post] = []
        
        with Pool() as pool:
            start = datetime.now()
            _posts_chunks = pool.map(self.extract_posts_from_html, thread_html)
            for chunk in _posts_chunks:
                _posts += chunk
            print(f"Extracted {len(_posts)} posts in {datetime.now() - start} multi-core")
                    
        return _posts
    
    def extract_posts_from_html(self, html: str) -> list["Post"]:
        """
        Extracts posts from HTML and returns a list of Post objects.
        """
        _posts: list[Post] = []
        
        soup = BeautifulSoup(html, "html.parser")
        thread_id_src = soup.find_all(
            "div", class_="block-container lbContainer", recursive=True
        )[0].get("data-lb-id")
        thread_id: int = int(thread_id_src.split("-")[-1])

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
            _posts.append(
                Post(author, post_id, content, thread_id, time_posted)
            )
        # other posts
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

                # remove quotes
                for quote in inner_bb.find_all("blockquote"):
                    quote.decompose()
                # remove images
                for img in inner_bb.select("div.bbImageWrapper"):
                    img.decompose()
                # remove inline videos
                for video in inner_bb.select("div.bbMediaWrapper"):
                    video.decompose()
                # remove youtube videos
                for video in inner_bb.select("span[data-s9e-mediaembed=\"youtube\"]"):
                    video.decompose()
                # remove embed websites
                for embed in inner_bb.select("div.bbCodeBlock"):
                    embed.decompose()
                
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
            Converts the posts data into a pandas DataFrame. Drops duplicates based on the post id.

            Returns:
                pd.DataFrame: A DataFrame containing the posts data.
            """
            df = pd.DataFrame(self.posts)
            df.drop_duplicates(subset="id", inplace=True)
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

