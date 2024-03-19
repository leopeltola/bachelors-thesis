import pandas as pd
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from numpy import ndarray


def topic_model_lda(data: pd.Series) -> None:  # type: ignore
    print("\n--- Starting LDA topic modelling ---")
    # from https://blog.mlreview.com/topic-modeling-with-scikit-learn-e80d33668730
    # LDA can only use raw term counts for LDA because it is a probabilistic graphical model
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words="english")
    tf = tf_vectorizer.fit_transform(data)  # type: ignore
    tf_feature_names = tf_vectorizer.get_feature_names_out()  # type: ignore

    lda = LatentDirichletAllocation(
        n_components=5,
    )
    w = lda.fit_transform(tf)  # type: ignore
    print("w:", w.shape)  # type: ignore
    df = pd.DataFrame(w)
    print(df)

    display_topics(lda, tf_feature_names, 20)
    print("--- LDA topic modelling complete ---\n")


def topic_model_nmf(data: pd.Series) -> None:  # type: ignore
    print("\n--- Starting NMF topic modelling ---")
    # NMF is able to use tf-idf
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words="english")
    tfidf = tfidf_vectorizer.fit_transform(data)  # type: ignore
    tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()  # type: ignore

    nmf = NMF(n_components=10, random_state=1)
    w = nmf.fit_transform(tfidf)  # type: ignore
    print("w:", w.shape)  # type: ignore
    df = pd.DataFrame(w)
    print(df)

    display_topics(nmf, tfidf_feature_names, 20)  # type: ignore
    print("--- NMF topic modelling complete ---\n")


def display_topics(model: NMF | LatentDirichletAllocation, feature_names: ndarray, no_top_words: int):  # type: ignore
    # from https://blog.mlreview.com/topic-modeling-with-scikit-learn-e80d33668730
    for topic_idx, topic in enumerate(model.components_):  # type: ignore
        print("Topic %d:" % (topic_idx))
        print(
            " ".join(
                [feature_names[i] for i in topic.argsort()[: -no_top_words - 1 : -1]]  # type: ignore
            )
        )
