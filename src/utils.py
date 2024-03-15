from pathlib import Path
import pandas as pd


def print_progress_bar(
    iteration: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 100,
    fill: str = "█",
    printEnd: str = "\r",
):
    """
    Call in a loop to create terminal progress bar

    Args:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def load_data_from_csv(
    posts_paths: list[Path], threads_paths: list[Path]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load data from CSV files and return DataFrames.

    Args:
        posts_paths (list[str]): List of file paths for posts CSV files.
        threads_paths (list[str]): List of file paths for threads CSV files.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two DataFrames:
            - posts: DataFrame containing data from all posts CSV files.
            - threads: DataFrame containing data from all threads CSV files.
    """
    # Posts
    posts_dfs: list[pd.DataFrame] = []
    for post in posts_paths:
        posts_dfs.append(pd.read_csv(post))  # type: ignore
    posts = pd.concat(posts_dfs)  # type: ignore
    # Threads
    threads_dfs: list[pd.DataFrame] = []
    for thread in threads_paths:
        threads_dfs.append(pd.read_csv(thread))  # type: ignore
    threads = pd.concat(threads_dfs)  # type: ignore

    return (posts, threads)
