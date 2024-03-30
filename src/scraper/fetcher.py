import asyncio

import aiohttp

from src.utils import print_progress_bar

BATCH_FETCHES = 50
BATCH_DELAY = 0.5  # seconds


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Fetches the content of a URL using an asynchronous HTTP GET request.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session to use for the request.
        url (str): The URL to fetch.

    Returns:
        str: The content of the URL.

    Raises:
        aiohttp.ClientResponseError: If the response status is not 200.
    """
    async with session.get(url) as response:
        if response.status != 200:
            response.raise_for_status()
        return await response.text()


async def fetch_all(session: aiohttp.ClientSession, urls: list[str]) -> list[str]:
    """
    Fetches multiple URLs asynchronously using the provided aiohttp ClientSession.

    Args:
        session (aiohttp.ClientSession): The aiohttp ClientSession to use for making requests.
        urls (list[str]): A list of URLs to fetch.

    Returns:
        list[str]: A list of fetched responses.

    """
    results: list[str] = []
    chunks: list[list[str]] = []
    if len(urls) > BATCH_FETCHES:
        for i in range(0, len(urls), BATCH_FETCHES):
            chunks.append(urls[i : i + BATCH_FETCHES])
    else:
        chunks.append(urls)

    batch_fetch = False
    if len(chunks) > 1:
        batch_fetch = True
        print(
            f"Fetching urls in {len(chunks)} chunks of {BATCH_FETCHES} w/ {BATCH_DELAY}s delay..."
        )

    for i, chunk in enumerate(chunks):
        tasks: list[asyncio.Task[str]] = []
        for url in chunk:
            task = asyncio.create_task(fetch(session, url))
            tasks.append(task)
        chunk_results = await asyncio.gather(*tasks)
        results += chunk_results
        if batch_fetch:
            await asyncio.sleep(BATCH_DELAY)
            print_progress_bar(
                i + 1, len(chunks), prefix="Fetching:", suffix="complete", decimals=2
            )
    return results
