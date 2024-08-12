import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo  
import requests
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#AlphaVantageAPI 
ALPHAVANTAGE_API_ENDPOINT = "https://www.alphavantage.co/query?"
ALPHAVANTAGE_APIKEY = "KE7MBHHWS14Q5O95"

#NewsAPI
NEWSAPI_ENDPOINT = 'https://newsapi.org/v2/everything?'
NEWSAPI_KEY = 'e566609b3a074d10891c172ccbcdcd62'

#Constants & Variables
STOCKS = ['AAPL', 'MSFT', 'HDFCBANK.BSE']    #Inital Stocks to display
GRAPHS = []    #for storing all objects 
ARTICLES = []    #for storing articles
LEN = 0 


#WTFORM to add to list STOCKS
class AddForm(FlaskForm):
    stock = StringField(label='name', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


#Class to create Graph object
class Graph():
    def __init__(self, name, df):
        self.name = name
        self.df = df
        self.process()  #Calculates Current Price, Difference and converts to datetime 

    def process(self):
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp']) #Converts timestamp to datetime type
        self.DELTA = round((self.df['open'][0] - self.df['open'][1]) / self.df['open'][0] * 100 , 3)    #Calculates difference between today and yesterday 
        self.price = self.df['open'][0] #Current Price
    
    def line(self):
        '''Create line graph and saves it as a html file in assets folder'''
        self.line = px.line(data_frame=self.df, 
                            x=self.df['timestamp'], 
                            y=self.df['open'], 
                            labels={'x':'', 'y':''}, 
                            title=f'{self.name}: {self.DELTA}%   Current Price: {self.df["open"][0]}', 
                            hover_data=['volume'], 
                            template="plotly_dark")
        pyo.plot(self.line, filename=rf'templates/{self.name}line.html')

    def candle(self):
        '''Create candlestick and saves it as a html file in assets folder'''
        self.candle = go.Figure(data=[go.Candlestick(
            x=self.df['timestamp'],
            open=self.df['open'],
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'])])
        pyo.plot(self.candle, filename=rf'templates/{self.name}candle.html')

        
def fetch_data(stock):
    '''GET request to alphavantage API to download csv and save it in assets'''
    parameters_daily = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': stock,
    'outputsize': 'compact',
    'apikey': ALPHAVANTAGE_APIKEY,
    'datatype': 'csv'
}
    response = requests.get(url=ALPHAVANTAGE_API_ENDPOINT, params=parameters_daily)
    if response.status_code == 200:
        daily_data = response.text
        with open(rf'static/assets/csv/{stock}.csv', mode='w') as file:
            file.write(daily_data)

def create_obj(stock):
    '''Reads the csv files and creates Graph object then appends to list GRAPHS'''
    df = pd.read_csv(rf'static/assets/csv/{stock}.csv')
    graph = Graph(df=df, name=stock)
    GRAPHS.append(graph)

def fetch_news(stock):
    '''GET request to newsAPI to fetch news articles and append them to list ARTICLES as json objects'''
    news_params = {
        'apiKey': NEWSAPI_KEY,
        'q': stock,
        'sortBy': 'relevancy',
        'language': 'en'
    }
    news_response = requests.get(NEWSAPI_ENDPOINT, params=news_params)
    news = news_response.json()
    if news_response.status_code == 200 and news['totalResults'] != 0:
        ARTICLES.append(news['articles'][0])
    global LEN
    LEN = len(ARTICLES)

def initialize():
    '''Downloads csv, creates Graph object and fetches news articles for all items in list STOCKS'''
    for stock in STOCKS:
        fetch_data(stock)
        create_obj(stock)
        fetch_news(stock)

def singular_initialize(stock):
    '''Downloads csv, creates Graph object and fetches news articles for the passed argument'''
    fetch_data(stock)
    create_obj(stock)
    fetch_news(stock)

initialize()    

app = Flask(__name__)    #Initiate Flask server
Bootstrap(app)    #Add Bootstrap to server
app.config['SECRET_KEY'] = '1j123h21ndu1jd19iackoac93328mcwnejd'

@app.route('/')
def home():
    return render_template('index.html', all_graphs = GRAPHS, all_articles=ARTICLES, len=LEN)

@app.route('/line/<name>')    
def line(name):
    for graph in GRAPHS:
        if graph.name == name:
            graph.line()
            return redirect(url_for('home'))

@app.route('/candle/<name>')    
def candle(name):
    for graph in GRAPHS:
        if graph.name == name:
            graph.candle()
            return redirect(url_for('home'))
        
@app.route('/add', methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        singular_initialize(form.stock.data)
        return redirect(url_for('home'))
    return render_template('add.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
