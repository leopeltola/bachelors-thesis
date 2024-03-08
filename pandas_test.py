from dataclasses import dataclass
import pandas as pd


@dataclass
class Data:
    author: str
    label: str
    id: int


items = [
    Data("author1", "label1", 1),
    Data("author2", "label2", 2),
    Data("author3", "label3", 3),
    Data("author4", "label4", 4),
    Data("author5", "label5", 5),
    Data("author6", "label6", 6),
    Data("author7", "label7", 7),
    Data("author8", "label8", 8),
    Data("author9", "label9", 9),
    Data("author10", "label10", 10),
]
df = pd.DataFrame(items)
df = df.set_index("author", drop=True)  # type: ignore
print(df)
print("\n", df.loc["author1"])  # type: ignore
