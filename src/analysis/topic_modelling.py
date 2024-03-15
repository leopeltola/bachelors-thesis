from pandas import Series
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def topic_model_lda(data: Series) -> None:  # type: ignore
    print("--- Starting LDA topic modelling ---")
    # from https://blog.mlreview.com/topic-modeling-with-scikit-learn-e80d33668730
    # LDA can only use raw term counts for LDA because it is a probabilistic graphical model
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words="english")
    tf = tf_vectorizer.fit_transform(data)  # type: ignore
    tf_feature_names = tf_vectorizer.get_feature_names_out()  # type: ignore

    lda = LatentDirichletAllocation(
        n_components=5,
        max_iter=5,
    ).fit(  # type: ignore
        tf
    )  # type: ignore
    display_topics(lda, tf_feature_names, 20)
    print("--- LDA topic modelling complete ---")


def topic_model_nmf(data: Series) -> None:  # type: ignore
    print("--- Starting NMF topic modelling ---")
    # NMF is able to use tf-idf
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words="english")
    tfidf = tfidf_vectorizer.fit_transform(data)  # type: ignore
    tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()  # type: ignore

    nmf = NMF(n_components=5, random_state=1, init="nndsvd").fit(  # type: ignore
        tfidf
    )  # type: ignore

    display_topics(nmf, tfidf_feature_names, 10)  # type: ignore
    print("--- NMF topic modelling complete ---")


def display_topics(model, feature_names, no_top_words: int):  # type: ignore
    # from https://blog.mlreview.com/topic-modeling-with-scikit-learn-e80d33668730
    for topic_idx, topic in enumerate(model.components_):  # type: ignore
        print("Topic %d:" % (topic_idx))
        print(
            " ".join(
                [feature_names[i] for i in topic.argsort()[: -no_top_words - 1 : -1]]  # type: ignore
            )
        )
