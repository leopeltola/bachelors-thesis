import asyncio
import pandas as pd
from forum import Website


if __name__ == "__main__":
    website = Website("https://incels.is")
    # asyncio.run(website.load_forum("inceldom-discussion", 2))
    asyncio.run(website.load_forum("must-read-content", 23))
    df = pd.DataFrame(website.threads)
    df.set_index("id", drop=True, inplace=True)  # type: ignore
    print(df)
