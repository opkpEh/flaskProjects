import feedparser 
from flask import Flask

app= Flask(__name__)

RSS_FEED= {
        "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
        "cnn": "http://rss.cnn.com/rss/edition.rss",
        "fox": "https://moxie.foxnews.com/google-publisher/latest.xml",
        "db": "https://www.bhaskar.com/rss-v1--category-4587.xml",
}
def get_news(publication):
    feed= feedparser.parse(RSS_FEED[publication])
    first_article= feed['entries'][0]
    return f"""<html>
                <body>
                    <h1>{publication} Headlines </h1>
                    <b> {first_article.get("title")}</b> <br/>
                    <i> {first_article.get("published")}</i> <br/>
                    <p> {first_article.get("summary")}</p> <br/>
                </body>
              </html> """


@app.route("/")
def index():
    return """<pre><h1 style= "color: red" >Home page to get RRS feed from: 
bbc 
cnn 
fox
db</h1></pre>"""

@app.route("/<publication>")
def get_news_publication(publication):
    return get_news(publication)


if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
