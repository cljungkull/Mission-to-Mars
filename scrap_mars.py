import pymongo
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
from pprint import pprint
from time import sleep

conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

db = client.mission_to_mars
collection = db.mission_to_mars

def scrape():

   
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)
    
    # Run the function below:
    first_title, first_paragraph = mars_news(browser)
    
    # Run the functions below and store into a dictionary
    results = {
        "title": first_title,
        "paragraph": first_paragraph,
        "image_URL": jpl_image(browser),
        "weather": mars_weather_tweet(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemis(browser),
    }

    # Quit the browser and return the scraped results
    browser.quit()
    return results

def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    mars_news_soup = BeautifulSoup(html, 'html.parser')

    # Scrape the first article title and teaser paragraph text; return them
    first_title = mars_news_soup.find('div', class_='content_title').text
    first_paragraph = mars_news_soup.find('div', class_='article_teaser_body').text
    return first_title, first_paragraph

def jpl_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Go to 'FULL IMAGE', then to 'more info'
    browser.click_link_by_partial_text('FULL IMAGE')
    sleep(1)
    browser.click_link_by_partial_text('more info')

    html = browser.html
    image_soup = BeautifulSoup(html, 'html.parser')

    # Scrape the URL and return
    feat_img_url = image_soup.find('figure', class_='lede').a['href']
    feat_img_full_url = f'https://www.jpl.nasa.gov{feat_img_url}'
    return feat_img_full_url

def mars_weather_tweet(browser):
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    html = browser.html
    tweet_soup = BeautifulSoup(html, 'html.parser')
    
    # Scrape the tweet info and return
    first_tweet = tweet_soup.find('p', class_='TweetTextSize').text
    return first_tweet
    
def mars_facts():
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['Property', 'Value']
    # Set index to property in preparation for import into MongoDB
    df.set_index('Property', inplace=True)
    
    # Convert to HTML table string and return
    return df.to_html()



#Mars Hemispheres
# URL of page to be scraped

def Mars_hemi(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    hemi_soup = BeautifulSoup(html, 'html.parser')

    # Retreive all items that contain mars hemispheres information
    items = soup.find_all('div', class_='item')

    # Create empty list for hemisphere urls 
    hemisphere_image_urls = []

    # Store the main_ul 
    hemispheres_main_url = 'https://astrogeology.usgs.gov'

    # Loop through the items previously stored
    for i in items: 
        title = i.find('h3').text
    
    # Store link that leads to full image website
        partial_img_url = i.find('a', class_='itemLink product-item')['href']
    
    # Visit the link that contains the full image website 
        browser.visit(hemispheres_main_url + partial_img_url)
    
    # HTML Object of individual hemisphere information website 
        partial_img_html = browser.html
    
    # Parse HTML with Beautiful Soup for every individual hemisphere information website 
        soup = BeautifulSoup( partial_img_html, 'html.parser')
    
    # Retrieve full image source 
        img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
    
    # Append the retreived information into a list of dictionaries 
        hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
    
    # Display hemisphere_image_urls
    return hemisphere_image_urls

from flask import Flask, render_template
# Import scrape_mars

import scrape_mars

# Import our pymongo library, which lets us connect our Flask app to our Mongo database.
import pymongo

# Create an instance of our Flask app.
app = Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017/mission_to_mars'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Set route
@app.route("/")
def index():
    mars = client.db.mars.find_one()
    return render_template("index.html", mars=mars)

# Scrape 
@app.route("/scrape")
def scrape():
    mars = client.db.mars
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data)
    return "Done!"

if __name__ == "__main__":
    app.run(debug=True)