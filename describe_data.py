"""Analyzes the processed data and generates visualizations."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from src.analysis.feminism import compute_feminism_scores


def plot_variables(posts: pd.DataFrame, var1: str, var2: str) -> None:
    """
    Plot two variables against each other.
    """
    posts = posts.sample(10000)
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.scatter(posts[var1], posts[var2], alpha=0.5)
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)
    ax.set_title(f"{var1} vs. {var2}")
    plt.show()


if __name__ == "__main__":
    print("Loading data...")
    posts = pd.read_csv("data/import/posts.csv")
    users = pd.read_csv("data/import/users.csv")
    threads = pd.read_csv("data/import/threads.csv")

    print(users.describe())
    print(
        "Users with >50 posts:",
        len(users[users["num_posts_by_user"] > 50]),
        "out of",
        len(users),
    )

    print(posts.describe())
    # get the max and min date_posted
    print(posts["date_posted"].max())
    print(posts["date_posted"].min())

    # sort users by number of posts
    users.sort_values(by="num_posts_by_user", ascending=False, inplace=True)
    print(users.head(20))
