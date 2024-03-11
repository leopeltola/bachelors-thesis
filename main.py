from src.forum import Website

MUST_READ = ("must-read-content", 23)
LOUNGE = ("the-lounge", 4)
INCEDLOM_DISCUSSION = ("inceldom-discussion", 2)

if __name__ == "__main__":
    website = Website("https://incels.is")
    website.load_and_save_forum(*MUST_READ)
    # website.load_and_save_forum(*LOUNGE)
    # website.load_and_save_forum(*INCEDLOM_DISCUSSION)
