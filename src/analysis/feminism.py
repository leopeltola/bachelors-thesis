import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

pd.options.mode.copy_on_write = True

feminism_keywords = [  # TODO: research how vectorization interacts with whitespace
    "feminism",
    "feminist",
    "gender equality",
    "women's rights",
    "patriarchy",
    "misogyny",
    "misogynistic",
    "sexism",
    "sexist",
    "glass ceiling",
    "gender pay gap",
    "reproductive rights",
    "intersectionality",
    "intersectional",
    "male privilege",
    "manspreading",
    "manspread",
    "gender roles",
    "gender norms",
    "gender bias",
    "gender discrimination",
    "women's empowerment",
    "female empowerment",
    "gender equity",
]


def compute_feminism_scores(posts: pd.DataFrame) -> pd.DataFrame:
    """
    Compute feminism scores for a given set of posts.

    Parameters:
    posts (pd.DataFrame): A DataFrame containing the posts to compute feminism scores for.

    Returns:
    pd.DataFrame: A DataFrame with the computed feminism scores.
    """
    # TF-IDF Vectorization
    vectorizer = CountVectorizer(stop_words="english", vocabulary=feminism_keywords)
    posts_vector = vectorizer.fit_transform(posts["content"])
    # Create column in posts for "content" word count
    posts["word_count"] = posts["content"].apply(lambda x: len(x.split()))
    # Compute feminism counts for each post as an pd.Series
    feminism_counts = pd.Series(posts_vector.toarray().sum(axis=1))  # type: ignore
    # Compute feminism scores for each post. The score is the sum of the counts of the feminism keywords in the post relative to the total number of words in the post.
    print(feminism_counts)
    print(posts["word_count"])
    feminism_scores = feminism_counts / posts["word_count"]
    # normalize the scores
    feminism_scores = (feminism_scores - feminism_scores.min()) / (
        feminism_scores.max() - feminism_scores.min()
    )
    posts["feminism_score"] = feminism_scores

    return posts


if __name__ == "__main__":
    # Create a mock dataframe with "content" column and compute feminism scores
    df = pd.DataFrame(
        [
            "Example text to test whether a string contains feminism and feminist keywords",
            "why is github copilot not working",
            "feminism is a social movement",
            "feminism is a social movement that advocates",
            "this does not contain anything",
            "misogyny is a social issue",
        ],
        columns=["content"],
    )
    df = compute_feminism_scores(df)
    print(df)
