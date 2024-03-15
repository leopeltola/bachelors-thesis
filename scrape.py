from src.forum import Website

FORUMS = [
    ("must-read-content", 23),
    ("the-lounge", 4),
    ("inceldom-discussion", 2),
]

if __name__ == "__main__":
    website = Website("https://incels.is")
    for forum in FORUMS:
        website.load_and_save_forum(*forum)
