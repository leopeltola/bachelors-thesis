import pandas as pd
import torch
from detoxify import Detoxify

pd.options.mode.copy_on_write = True


def toxicity_analysis(data: pd.DataFrame) -> pd.DataFrame:
    """Toxicity analysis using Detoxify. Modifies the passed dataframe in place, adding to it the toxicity scores."""
    # A naive implementation. May crash with large datasets -> partition if needed
    # Check if data parameter has any non-string in "content" column
    # count NaNs in content column
    if data["content"].isnull().sum() > 0:
        raise ValueError("Dataframe contains NaNs in content column")

    model = Detoxify("unbiased", device="cuda" if torch.cuda.is_available() else "cpu")
    # partition data into smaller chunks and process them individually, then concatenate the results
    chunk_size = 100
    chunks = [data.iloc[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
    print(
        "Computing toxicity scores in {} chunks with {}".format(
            len(chunks), model.device
        )
    )
    for i, chunk in enumerate(chunks):
        scores = model.predict(chunk["content"].tolist())
        chunk["severe_toxicity"] = scores["severe_toxicity"]
        chunk["toxicity"] = scores["toxicity"]
        chunk["sexual_explicit"] = scores["sexual_explicit"]

    # concatenate the chunks back into the original dataframe
    data = pd.concat(chunks)
    return data


if __name__ == "__main__":
    df = pd.DataFrame(
        [
            "hi there",
            "i'll kill you",
            "Kill yourself faggot op for reminding me of this shit",
            "My example is touching one foid's ass on purpose when i was in grade 7.",
        ],
        columns=["content"],
    )
    print(df)
    df = toxicity_analysis(df)
    print(df)
