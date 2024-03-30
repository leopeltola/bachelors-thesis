"""Analyzes the processed data and generates visualizations."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if __name__ == "__main__":
    posts = pd.read_csv("data/posts.csv")
    users = pd.read_csv("data/users.csv")
    threads = pd.read_csv("data/threads.csv")

    posts.sort_values(by="severe_toxicity", ascending=False, inplace=True)
    print(posts)
    posts.sort_values(by="severe_toxicity", ascending=True, inplace=True)
    print(posts)

    # Pearson correlation between nth_post_by_user and severe_toxicity
    print(
        "Nth post by user & severe toxicity Pearson correlation:",
        posts["nth_post_by_user"].corr(posts["severe_toxicity"]),
    )
    # Pearson correlation between nth_post_by_user and sexual_explicit
    print(
        "Nth post by user & sexual explicit Pearson correlation:",
        posts["nth_post_by_user"].corr(posts["sexual_explicit"]),
    )
    # Spearman correlation between nth_post_by_user and severe_toxicity
    print(
        "Nth post by user & severe toxicity Spearman correlation:",
        posts["nth_post_by_user"].corr(posts["severe_toxicity"], method="spearman"),
    )
    # Spearman correlation between nth_post_by_user and sexual_explicit
    print(
        "Nth post by user & sexual explicit Spearman correlation:",
        posts["nth_post_by_user"].corr(posts["sexual_explicit"], method="spearman"),
    )

    var = "severe_toxicity"
    plt.scatter(posts["nth_post_by_user"], posts[var], s=0.05)
    plt.xlabel("Nth post by user")
    plt.ylabel(var)
    z = np.polyfit(posts["nth_post_by_user"], posts[var], 1)
    p = np.poly1d(z)
    plt.plot(posts["nth_post_by_user"], p(posts[var]), "r--")
    plt.show()
