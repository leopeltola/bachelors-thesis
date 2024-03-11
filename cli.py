import asyncio
from datetime import datetime
import click

from src.forum import Website


@click.group()
def cli():
    pass


@click.command()
@click.argument("label", type=str)
@click.argument("id", type=int)
def load_forum(forum_label: str, id: int):
    website = Website("https://incels.is")
    # asyncio.run(website.load_forum("inceldom-discussion", 2))
    start = datetime.now()
    try:
        asyncio.run(website.load_forum("must-read-content", 23))
    except Exception as e:
        # dump saved stuff to disk
        print("Error loading forum: ", e)
        website.threads_as_dataframe().to_csv(f"{id}_threads.csv")
        website.posts_as_dataframe().to_csv(f"{id}_posts.csv")
        return
    # asyncio.run(website.load_forum("the-lounge", 4))
    print("\nLoading forum took {} seconds".format((datetime.now() - start).seconds))
    threads = website.threads_as_dataframe()
    print(threads)
    posts = website.posts_as_dataframe()
    print(posts)
    threads.to_csv(f"{id}_threads.csv")
    posts.to_csv(f"{id}_posts.csv")


@cli.command()
@cli.argument("msg")  # type: ignore
def hello(msg: str):
    click.echo("Hello world: ", msg)


cli.add_command(load_forum)
