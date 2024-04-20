import pandas as pd
import statsmodels.api as sm

from src.analysis.feminism import (
    compute_feminism_scores,
    compute_incel_scores,
    compute_sexual_scores,
)

if __name__ == "__main__":
    print("Loading data...")
    posts = pd.read_csv("data/import/posts.csv")

    print(posts)
    # drop nans
    posts.dropna(subset=["content"], inplace=True)

    # plot_prev = sm.qqplot(posts["feminism_score"].sample(100_000), line="s")
    # plot_prev.show()
    print("Computing feminism scores...")
    posts = compute_feminism_scores(posts)
    print("Computing sexual scores...")
    posts = compute_sexual_scores(posts)
    print("Computing incel scores...")
    posts = compute_incel_scores(posts)
    # plot = sm.qqplot(posts["feminism_score"].sample(100_000), line="s")
    # plot.show()

    # drop nans
    posts.dropna(subset=["feminism_score", "sexual_score", "incel_score"], inplace=True)

    posts.to_csv("data/import/posts2.csv")
    print(posts)

    input("Press Enter to continue...")
