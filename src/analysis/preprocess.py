import re

import nltk
import numpy as np
import pandas as pd


def lemmatize(text):
    lemmatizer = nltk.WordNetLemmatizer()
    wstokenizer = nltk.WhitespaceTokenizer()
    return " ".join([lemmatizer.lemmatize(word) for word in wstokenizer.tokenize(text)])


def preprocess(data: pd.DataFrame) -> None:
    # Assure that the content column is of type string
    data["content"] = data["content"].astype(str)
    # Remove duplicates
    data.drop_duplicates(subset=["id"], inplace=True)
    # Remove punctuation
    data["content"] = data["content"].map(lambda x: x.replace("'", ""))
    data["content"] = data["content"].map(lambda x: re.sub("[,\\.!?]", "", str(x)))
    # Remove urls
    data["content"] = data["content"].map(
        lambda x: re.sub(r"^https?:\/\/.*[\r\n]*", "", str(x))
    )
    # Convert the titles to lowercase and strip leading/trailing white space
    data["content"] = data["content"].map(lambda x: x.lower().strip())
    # Remove stop words
    stop_words = set(nltk.corpus.stopwords.words("english"))
    data["content"] = data["content"].map(
        lambda x: " ".join([word for word in x.split() if word not in stop_words])
    )
    # Replace empty string in content with NaN
    data["content"] = data["content"].replace("", np.nan)
    # Drop rows with NaN in content
    data.dropna(
        subset=["content"],
        inplace=True,
    )
    # Lemmatize
    data["content"] = data["content"].map(lemmatize)
    # Replace string "nan" with NaN
    data["content"] = data["content"].replace("nan", np.nan)
    data.dropna(
        subset=["content"],
        inplace=True,
    )


if __name__ == "__main__":
    # Test the preprocess function
    data = pd.DataFrame(
        ["man", "men"],
        columns=["content"],
    )
    print(data)
    preprocess(data)
    wnl = nltk.WordNetLemmatizer()
    print(data)
