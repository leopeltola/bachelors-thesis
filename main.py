import asyncio

from forum import Website


if __name__ == "__main__":
    website = Website("https://incels.is")
    # asyncio.run(website.load_forum("inceldom-discussion", 2))
    asyncio.run(website.load_forum("must-read-content", 23))
