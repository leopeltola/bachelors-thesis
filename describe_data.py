from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.preprocess import preprocess
from src.analysis.toxic import compute_toxicity_and_sexuality_scores
from src.utils import load_data_from_csv

# pd.options.plotting.backend = "plotly"
pd.options.mode.copy_on_write = True

if __name__ == "__main__":
    # load forum dataframes from .csv files
    path = Path("data")
    print("Loading data...")
    posts, threads = load_data_from_csv(
        [path / "import/posts_dump.csv.zip"],
        [
            path / "import/threads_the-lounge_4.csv.zip",
        ],
    )

    # Preprocess data
    print(posts)
    print("Preprocessing data...")
    start = datetime.now()
    preprocess(posts)
    print(f"Preprocessing took: {datetime.now() - start}\n")

    # Compute unique authors from posts
    unique_authors = posts["author"].unique()  # type: ignore
    users = pd.DataFrame(unique_authors, columns=["author"])
    users.set_index("author", inplace=True)  # type: ignore
    # Generate new "num_posts_by_user" column
    users["num_posts_by_user"] = posts["author"].value_counts()  # type: ignore
    users.sort_values(by="num_posts_by_user", ascending=False, inplace=True)  # type: ignore

    # Generate new "nth_post_by_user" column
    posts["nth_post_by_user"] = posts.groupby("author").cumcount() + 1  # type: ignore

    # Debug Preview data
    # print(users.describe(include="all"))
    # print(users[users["num_posts_by_user"] > 50].count())  # type: ignore

    print("Nans in data: ", posts.isna().sum())
    start = datetime.now()
    # posts = compute_toxicity_and_sexuality_scores(posts)
    # print(f"Toxicity analysis took: {datetime.now() - start}\n")

    # posts.to_csv("data/posts.csv")
    # users.to_csv("data/users.csv")
    # threads.to_csv("data/threads.csv")
    print(posts)
