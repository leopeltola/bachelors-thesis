from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.preprocess import preprocess
from src.analysis.topic_modelling import topic_model_lda, topic_model_nmf  # type: ignore
from src.analysis.wordcloud import wordcloud  # type: ignore
from src.utils import load_data_from_csv

pd.options.plotting.backend = "plotly"


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

    # Preprocess data
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

    # Preview data
    print(users.describe(include="all"))
    print(users[users["num_posts_by_user"] > 50].count())  # type: ignore

    # print number of nans
    # print(posts["content"].isna().sum())  # type: ignore
    # print(posts["content"].count())  # type: ignore
    # print(posts)
    # print(posts.describe())

    # topic_model_nmf(posts["content"])
    # topic_model_lda(posts["content"])
    wordcloud(posts["content"])
