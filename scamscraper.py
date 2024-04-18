from langchain_community.document_loaders import WebBaseLoader
import requests
from bs4 import BeautifulSoup
import re  

def scrape_scam_stories():
    url = "https://www.scamalert.sg/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the news cards
    news_cards = soup.select('#divNewsList .col-md-4')
    news_cards = news_cards[:3]
    scam_stories = []

    # Extract the news title and link from each card
    for card in news_cards:
        title_element = card.select_one('.card-title a')
        title = title_element.text.strip() if title_element else "N/A"

        link_element = card.select_one('.card-title a')
        link = link_element['href'] if link_element else "N/A"

        scam_stories.append({"title": title, "link": link})

    print("Scam stories scraped:", scam_stories)

    first_read_more_link = scrape_first_read_more_link()
    print("First read more link scraped:", first_read_more_link)
    article_info = []

    for article in scam_stories:
        title = article['title']
        link = article['link']

        try:
            loader = WebBaseLoader(link)
            text = loader.load()[0].page_content
            cleaned_text = clean_text(text)  # Clean the text using the defined function

            article_info.append({
                'title': title,
                'link': link,
                'text': cleaned_text
            })
        except Exception as e:
            print(f"Error loading article: {title}")
            print(f"Error message: {str(e)}")

    return article_info, first_read_more_link

def clean_text(text):
    # Replace multiple newlines with a single newline, then strip leading/trailing whitespace
    return re.sub(r'\n\s*\n', '\n', text).strip()

def scrape_first_read_more_link():
    url = "https://www.police.gov.sg/Media-Room/Scams-Bulletin"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    newscards_list = soup.find("div", class_="newscards__list")
    if newscards_list:
        first_newscard = newscards_list.find("div", class_="newscard")
        if first_newscard:
            read_more_link = first_newscard.find("a")["href"]
            return read_more_link

    return None
