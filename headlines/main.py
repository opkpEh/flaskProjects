import feedparser 
from flask import Flask, render_template, request 

app= Flask(__name__)

RSS_FEED= {
        "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
        "fox": "https://moxie.foxnews.com/google-publisher/latest.xml",
        "db": "https://www.bhaskar.com/rss-v1--category-4587.xml",
}

@app.route("/",methods=["GET","POST"])
def get_news():
    query= request.form.get("publication") #use args instead of from for GET
   
    if not query or query.lower() not in RSS_FEED:
        publication= "bbc"
    else:
        publication= query.lower()
    
    feed= feedparser.parse(RSS_FEED[publication])
    
    return render_template("headline.html",headline=publication, articles=feed['entries'])

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
