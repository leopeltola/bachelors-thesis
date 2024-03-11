import aiohttp
import asyncio

BATCH_FETCHES = 5
BATCH_DELAY = 0.4  # seconds


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        aiohttp.ClientResponse
        if response.status != 200:
            response.raise_for_status()
        return await response.text()


async def fetch_all(session: aiohttp.ClientSession, urls: list[str]) -> list[str]:
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
            print(f"Fetched chunk {i + 1}/{len(chunks)}...")
    return results
