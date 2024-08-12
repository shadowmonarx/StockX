import os
from dotenv import load_dotenv
import requests
import pandas as pd
from Graph import Graph

load_dotenv()

def fetch_data(stock: str) -> None:
    '''GET request to alphavantage API to download csv and save it in assets'''
    parameters_daily: dict[str, str] = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': stock,
    'outputsize': 'compact',
    'apikey': os.getenv('ALPHAVANTAGE_APIKEY'),
    'datatype': 'csv'
}
    response: requests.Response = requests.get(url=os.getenv('ALPHAVANTAGE_API_ENDPOINT'), params=parameters_daily)
    if response.status_code == 200:
        daily_data: str = response.text
        with open(rf'static/assets/csv/{stock}.csv', mode='w') as file:
            file.write(daily_data)

def fetch_news(stock: str):
    '''GET request to newsAPI to fetch news articles and append them to list ARTICLES as json objects'''
    news_params: dict[str, str] = {
        'apiKey': os.getenv('NEWSAPI_KEY'),
        'q': stock,
        'sortBy': 'relevancy',
        'language': 'en'
    }
    news_response: requests.Response = requests.get(os.getenv('NEWSAPI_ENDPOINT'), params=news_params)
    news = news_response.json()
    if news_response.status_code == 200 and news['totalResults'] != 0:
       return news['articles'][0]

def create_obj(stock: str) -> Graph:
    '''Reads the csv files and creates Graph object then appends to list GRAPHS'''
    df: pd.DataFrame = pd.read_csv(rf'static/assets/csv/{stock}.csv')
    graph: Graph = Graph(df=df, name=stock)
    return graph
