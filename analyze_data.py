"""Analyzes the processed data and generates visualizations."""

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from tabulate import tabulate


def correlation(posts: pd.DataFrame, var1: str, var2: str) -> None:
    """
    Compute Pearson and Spearman correlation between two variables in a DataFrame.
    """
    # count NaN values
    # print(f"{var1} NaN count:", posts[var1].isna().sum())  # returns 0?
    # drop NaN values
    posts = posts.dropna(
        subset=[var1, var2]
    )  # doesn't seem to do anything but pearsonr raises an error without...
    # Correlation coefficients
    pearson_corr = stats.pearsonr(posts[var1], posts[var2])
    spearman_corr = stats.spearmanr(posts[var1], posts[var2])

    # calculate confidence interval for Spearman correlation
    def compute_spearman_ci(r: float, num: int) -> tuple[float, float]:
        stderr = 1.0 / math.sqrt(num - 3)
        delta = 1.96 * stderr
        lower = math.tanh(math.atanh(r) - delta)
        upper = math.tanh(math.atanh(r) + delta)
        return (lower, upper)

    print(
        f"{var1} & {var2}\n",
        tabulate(
            [
                [
                    "Pearson",
                    pearson_corr.statistic,  # type: ignore
                    pearson_corr.pvalue,  # type: ignore
                    pearson_corr.confidence_interval(95),  # type: ignore
                ],
                [
                    "Spearman",
                    spearman_corr.statistic,  # type: ignore
                    spearman_corr.pvalue,  # type: ignore
                    compute_spearman_ci(
                        spearman_corr.correlation, len(posts)  # type: ignore
                    ),
                ],
            ],
            headers=["Variables", "Correlation", "Coefficient", "P-value", "CI"],
        ),
        "\n",
    )


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


def line_plot(posts: pd.DataFrame, var1: str, var2: str) -> None:
    """
    Plot two variables against each other.
    """
    posts = posts.sample(10000)
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(posts[var1], posts[var2], alpha=0.5)
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)
    ax.set_title(f"{var1} vs. {var2}")
    plt.show()


def linear_regression(
    posts: pd.DataFrame, dependent_var: str, independent_var: str
) -> None:
    """
    Compute linear regression between two variables in a DataFrame.
    """
    # Fit the model
    model = smf.ols(f"{dependent_var} ~ {independent_var}", posts).fit()
    print(model.params)
    print(model.summary())


if __name__ == "__main__":
    print("Loading data...")
    posts = pd.read_csv("data/import/posts2.csv")
    users = pd.read_csv("data/import/users.csv")
    threads = pd.read_csv("data/import/threads.csv")

    print(posts)

    threshold = 0
    if threshold:
        # print the number of posts by users with > threshold posts
        users_count = len(users[users["num_posts_by_user"] > threshold])
        print(f"Users with >{threshold} posts:", users_count, "out of", len(users))
        # remove posts by users with > threshold posts
        users = users[users["num_posts_by_user"] < threshold]
        posts = posts[posts["author"].isin(users["author"])]

    # posts.sort_values(by="severe_toxicity", ascending=False, inplace=True)
    # print(posts)
    # top_toxic_posts = posts.head(10)
    # for index, row in top_toxic_posts.iterrows():
    #     print(row["content"])
    #     print(row["severe_toxicity"])
    #     print(row["id"])
    #     print()
    # posts.sort_values(by="severe_toxicity", ascending=True, inplace=True)

    print(users.describe())

    plot = sm.qqplot(posts["severe_toxicity"].sample(20_000), line="s")
    plot.savefig(Path("img") / "qqplot_severe_toxicity.png")
    plot = sm.qqplot(posts["sexual_explicit"].sample(20_000), line="s")
    plot.savefig(Path("img") / "qqplot_sexual_explicit.png")
    plot = sm.qqplot(posts["feminism_score"].sample(20_000), line="s")
    plot.savefig(Path("img") / "qqplot_feminism_score.png")
    plot = sm.qqplot(posts["sexual_score"].sample(20_000), line="s")
    plot.savefig(Path("img") / "qqplot_sexual_score.png")
    plot = sm.qqplot(posts["incel_score"].sample(20_000), line="s")
    plot.savefig(Path("img") / "qqplot_incel_score.png")

    print("\nCorrelation coefficients:")
    correlation(posts, "nth_post_by_user", "severe_toxicity")
    correlation(posts, "nth_post_by_user", "sexual_explicit")
    correlation(posts, "nth_post_by_user", "feminism_score")
    correlation(posts, "nth_post_by_user", "sexual_score")
    correlation(posts, "nth_post_by_user", "incel_score")

    # print("\nLinear regression:")
    # linear_regression(posts, "severe_toxicity", "nth_post_by_user")
    # linear_regression(posts, "sexual_explicit", "nth_post_by_user")
    # linear_regression(posts, "feminism_score", "nth_post_by_user")
    # linear_regression(posts, "sexual_score", "nth_post_by_user")

    # create a dataframe with the average toxicity score for each post rank order number (eg. 1st post, 2nd post, etc.)
    # average_toxicity = posts.groupby("nth_post_by_user")["severe_toxicity"].mean()
    # print(average_toxicity)

    # plot the average toxicity score for each post rank order number as a histogram in ten bins. Y axis is mean toxicity score, X axis is grouped post rank order number.
    # fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    # ax.hist(average_toxicity, bins=10)
    # ax.set_xlabel("Post rank order number")
    # ax.set_ylabel("Mean toxicity score")
    # ax.set_title("Mean toxicity score for each post rank order number")
    # plt.show()

    # Plot the data
    # plot_variables(posts.sample(30_000), "nth_post_by_user", "severe_toxicity")
    # line_plot(posts.sample(30_000), "nth_post_by_user", "severe_toxicity")
    # plot_variables(posts, "nth_post_by_user", "feminism_score")
    # plot_variables(posts, "nth_post_by_user", "sexual_explicit")
