from pathlib import Path

import pandas as pd

from src.utils import load_data_from_csv


if __name__ == "__main__":
    # load forum dataframes from .csv files
    path = Path("data")

    posts, threads = load_data_from_csv(
        [
            path / "posts_must-read-content_03-11-2024_16.17.32.csv",
        ],
        [
            path / "threads_must-read-content_03-11-2024_16.17.32.csv",
        ],
    )

    # Compute unique authors from posts
    unique_authors = posts["author"].unique()  # type: ignore
    users = pd.DataFrame(unique_authors, columns=["author"])
    users.set_index("author", inplace=True)  # type: ignore
    # Generate new "num_posts_by_user" column
    users["num_posts_by_user"] = posts["author"].value_counts()  # type: ignore
    users.sort_values(by="num_posts_by_user", ascending=False, inplace=True)  # type: ignore

    # Generate new "nth_post_by_user" column
    posts["nth_post_by_user"] = posts.groupby("author").cumcount() + 1  # type: ignore

    # Preview data
    print(posts)
    print(users)
    print(posts.loc[posts["author"] == "Edmund_Kemper"])
