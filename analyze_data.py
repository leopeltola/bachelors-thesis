"""Analyzes the processed data and generates visualizations."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis.feminism import compute_feminism_scores


def correlation(posts: pd.DataFrame, var1: str, var2: str) -> None:
    """
    Compute Pearson and Spearman correlation between two variables in a DataFrame.
    """
    # Pearson correlation
    print(f"{var1} & {var2} Pearson correlation:", posts[var1].corr(posts[var2]))
    # Spearman correlation
    print(
        f"{var1} & {var2} Spearman correlation:",
        posts[var1].corr(posts[var2], method="spearman"),
    )


if __name__ == "__main__":
    posts = pd.read_csv("data/posts.csv")
    users = pd.read_csv("data/users.csv")
    threads = pd.read_csv("data/threads.csv")

    print(posts)
    # posts.to_csv("data/posts.csv")

    posts.sort_values(by="severe_toxicity", ascending=False, inplace=True)
    # print(posts)
    top_toxic_posts = posts.head(10)
    for index, row in top_toxic_posts.iterrows():
        print(row["content"])
        print(row["severe_toxicity"])
        print(row["id"])
        print()
    # posts.sort_values(by="severe_toxicity", ascending=True, inplace=True)

    correlation(posts, "nth_post_by_user", "severe_toxicity")
    correlation(posts, "nth_post_by_user", "feminism_score")
    correlation(posts, "nth_post_by_user", "sexual_explicit")

    # var = "severe_toxicity"
    # plt.scatter(posts["nth_post_by_user"], posts[var], s=0.05)
    # plt.xlabel("Nth post by user")
    # plt.ylabel(var)
    # z = np.polyfit(posts["nth_post_by_user"], posts[var], 1)
    # p = np.poly1d(z)
    # plt.plot(posts["nth_post_by_user"], p(posts[var]), "r--")
    # plt.show()
