import feedparser 
from flask import Flask, render_template, request 
import json 
from urllib.parse import quote
from urllib.request import urlopen

app= Flask(__name__)

RSS_FEED= {
        "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
        "fox": "https://moxie.foxnews.com/google-publisher/latest.xml",
        "db": "https://www.bhaskar.com/rss-v1--category-4587.xml",
}

DEFAULT_VALUE= {
        "publication": "bbc",
        "city": "Delhi,India"
}

@app.route("/", methods=["GET", "POST"])
def index():
    publication= request.form.get("publication")
    
    if not publication:
        publication = DEFAULT_VALUE["publication"] 
    
    print(publication)
    articles = get_news(publication)
    
    city = request.args.get("city")
    if not city:
        city = DEFAULT_VALUE["city"]
    
    weather = get_weather(city)
   
    return render_template("headline.html", headline=publication, articles=articles, weather=weather)

def get_news(query):
  
    if not query or query.lower() not in RSS_FEED:
        publication= DEFAULT_VALUE["publication"]
    else:
        publication= query.lower()
    
    feed= feedparser.parse(RSS_FEED[publication])

    return feed['entries']


def get_weather(query):
   
    with open("apiKey.txt", "r") as apiFile:
        api_key= apiFile.read().strip()

    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}"+"&units=metric&appid={0}".format(api_key)
    query = quote(query)
    url = api_url.format(query)
    data = urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"],
                   "country": parsed["sys"]["country"]}
    return weather

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
