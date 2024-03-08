import aiohttp
import asyncio


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        aiohttp.ClientResponse
        if response.status != 200:
            response.raise_for_status()
        return await response.text()


async def fetch_all(session: aiohttp.ClientSession, urls: list[str]):
    tasks: list[asyncio.Task[str]] = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results
