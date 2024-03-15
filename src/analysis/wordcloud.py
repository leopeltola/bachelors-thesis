from pandas import Series
from wordcloud import WordCloud  # type: ignore


def wordcloud(data: Series) -> None:  # type: ignore
    long_string = ",".join(list(data.dropna(inplace=False).values))  # type: ignore
    print("--- Generating word cloud ---")
    print("Nans in data: ", data.isna().sum())  # type: ignore
    print("Nans in data: ", long_string.count(" nan "))  # type: ignore
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
    wordcloud.generate(long_string)  # type: ignore
    # Visualize the word cloud
    img = wordcloud.to_image()  # type: ignore
    img.show()  # type: ignore
    img.save("wordcloud.png")  # type: ignore
