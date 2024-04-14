from langchain.document_loaders import WebBaseLoader

def scrape_scam_stories():
    loader = WebBaseLoader("https://www.scamalert.sg/stories")
    scam_stories = loader.load()
    print("Scam stories scraped: ", scam_stories)
    return scam_stories