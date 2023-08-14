import requests
from bs4 import BeautifulSoup
import csv
import matplotlib.pyplot as plt
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
import schedule
import time


class WebScrapingBot:
    def __init__(self):
        self.user_interface = UserInterface()
        self.data_processor = DataProcessor()
        self.data_storage = DataStorage()
        self.scheduler = Scheduler()
        self.error_handler = ErrorHandler()

    def run(self):
        self.user_interface.collect_search_query()
        search_query = self.user_interface.get_search_query()
        url = self.fetch_url(search_query)
        if url is not None:
            self.parse_web_page(url)
            self.process_data()
            self.store_data()
            self.visualize_data()
            self.schedule_task()

    def fetch_url(self, search_query):
        try:
            response = requests.get(f"https://www.google.com/search?q={search_query}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                url = soup.find('cite').get_text()
                return url
            else:
                self.error_handler.log_error("Failed to fetch URL.")
        except Exception as e:
            self.error_handler.log_error(str(e))

    def parse_web_page(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                images = soup.find_all('img')
                links = soup.find_all('a')
                self.data_processor.set_parsed_data(text, images, links)
            else:
                self.error_handler.log_error("Failed to parse web page.")
        except Exception as e:
            self.error_handler.log_error(str(e))

    def process_data(self):
        parsed_data = self.data_processor.get_parsed_data()
        if parsed_data is not None:
            text = parsed_data["text"]
            sia = SentimentIntensityAnalyzer()
            sentiment_scores = [sia.polarity_scores(sentence)["compound"] for sentence in nltk.sent_tokenize(text)]
            self.data_processor.set_processed_data(sentiment_scores)
        else:
            self.error_handler.log_error("No parsed data available for processing.")

    def store_data(self):
        processed_data = self.data_processor.get_processed_data()
        if processed_data is not None:
            with open("data.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Sentiment Score"])
                writer.writerows([[score] for score in processed_data])
        else:
            self.error_handler.log_error("No processed data available for storage.")

    def visualize_data(self):
        processed_data = self.data_processor.get_processed_data()
        if processed_data is not None:
            plt.plot(processed_data)
            plt.xlabel("Sentence Index")
            plt.ylabel("Sentiment Score")
            plt.title("Sentiment Analysis")
            plt.show()
        else:
            self.error_handler.log_error("No processed data available for visualization.")

    def schedule_task(self):
        self.scheduler.schedule(self.run)


class UserInterface:
    def __init__(self):
        self.search_query = ""

    def collect_search_query(self):
        self.search_query = input("Enter your search query: ")

    def get_search_query(self):
        return self.search_query


class DataProcessor:
    def __init__(self):
        self.parsed_data = None
        self.processed_data = None

    def set_parsed_data(self, text, images, links):
        self.parsed_data = {
            "text": text,
            "images": images,
            "links": links
        }

    def get_parsed_data(self):
        return self.parsed_data

    def set_processed_data(self, sentiment_scores):
        self.processed_data = sentiment_scores

    def get_processed_data(self):
        return self.processed_data


class DataStorage:
    def __init__(self):
        self.data = []

    def store_data(self, data):
        self.data.append(data)

    def get_data(self):
        return self.data


class Scheduler:
    def schedule(self, func):
        schedule.every(24).hours.do(func)
        while True:
            schedule.run_pending()
            time.sleep(1)


class ErrorHandler:
    def log_error(self, message):
        print(f"Error: {message}")


if __name__ == "__main__":
    # Create an instance of the WebScrapingBot class
    web_scraping_bot = WebScrapingBot()

    # Run the web scraping bot
    web_scraping_bot.run()