import numpy as np
from pandas import Series
from wordcloud import WordCloud
import nltk


def wordcloud(data: Series) -> None:
    # data.replace("nan", np.NaN, inplace=True)
    long_string = ",".join(list(data.loc[data.notnull()].values))
    print("--- Generating word cloud ---")
    print("Nans in data: ", data.isna().sum())
    print("Nans in datastring: ", long_string.count(",nan,"))
    # Create a WordCloud object
    wordcloud = WordCloud(
        background_color="white",
        max_words=5000,
        contour_width=3,
        contour_color="steelblue",
        height=800,
        width=1300,
    )
    # Generate a word cloud
    wordcloud.generate(long_string)
    # Visualize the word cloud
    img = wordcloud.to_image()
    img.show()
    img.save("wordcloud.png")
    print("--- Word cloud saved as wordcloud.png ---")
