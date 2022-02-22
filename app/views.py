"""
Handle requests.

Authors:
Majeed Malik
"""

from flask import render_template
import tweepy
from langdetect import detect
import spacy
from geopy.geocoders import Nominatim
import re
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')
nltk.download('wordnet')

def index():
    """Render Startpage."""
    markers = create_markers()
    return render_template("index.html", markers=markers)


def check_digits(word):
    counter = 0
    for char_count in range(len(word)):
        char = word[char_count]
        if char.isdigit():
            counter += 1
    if counter > (len(word)/2):
        return False
    else:
        return True

def preprocess(text, nlp, stop_words, blacklist):
  tokenizer = RegexpTokenizer(r'\w+')
  text_without_urls = re.sub('pic.twitter.com[^\s]*|(http|https):\/\/[^\s]*', '', text.lower())
  text_without_accounts_and_hashtag = re.sub('@\s[^\s]*|#\s[^\s]*|@[^\s]*', '', text_without_urls)
  tokens = tokenizer.tokenize(text_without_accounts_and_hashtag)
  tokens_without_stopwords = [token for token in tokens if not token in stop_words]
  tokens_without_blacklist = [token for token in tokens_without_stopwords if not token in blacklist]
  tokens_no_digits = [token for token in tokens_without_blacklist if not token.isdigit() and check_digits(token)]
  tokens_min_len = [token for token in tokens_no_digits if len(token) > 1]
  cleaned_text = []
  for token in tokens_min_len:
    doc = nlp(token)
    result = ' '.join([x.lemma_ for x in doc])
    cleaned_text.append(result)
  return ' '.join(cleaned_text)

def extract_gpe(cleansed_text, text, created_at, markers_pin, nlp, geolocator):
    doc = nlp(cleansed_text)
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            location = geolocator.geocode(ent.text)
            try:
                text = re.sub('[^A-Za-z0-9 +]+', '', text)
                obj = {
                    "text": text,
                    "GPE": str(ent.text),
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "created_at": created_at
                }
                markers_pin.append(obj)
            except:
                pass
    return markers_pin

def create_markers():
    geolocator = Nominatim(user_agent="Your_Name")
    client = tweepy.Client("<YOUR_BEARER_TOKEN>")
    id_users = ['28785486']
    list_of_tweets = []

    stop_words_en = stopwords.words('english')
    stop_words_de = stopwords.words('german')
    blacklist = ['http','https','www','com']

    stopwords_lists = {
        'en': stop_words_en,
        'de': stop_words_de
    }
    language_models = {
        'en': 'en_core_web_sm',
        'de': 'de_core_news_sm'
    }

    for user in id_users:
        # Replace with your own search query
        # query = 'from:OlafScholz -is:retweet'
        # tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'], max_results=100)
        response = client.get_users_tweets(id=user, exclude='retweets', max_results=100,  tweet_fields=['id','text','created_at', 'public_metrics', 'lang'])

        for page in response:
            for obj in page:
                try:
                    temp_dict = {}
                    temp_dict["text"] = str(obj["text"])
                    temp_dict["id"] = str(obj["id"])
                    temp_dict["created_at"] = str(obj["created_at"])
                    temp_dict["public_metrics"] = obj["public_metrics"]
                    temp_dict["lang"] = str(obj["lang"])
                    list_of_tweets.append(temp_dict)
                except:
                    pass

    current_language = ''
    markers_pin = []
    print(f"Total number of tweets: {len(list_of_tweets)}")
    counter = 0
    for tweet in list_of_tweets:
        counter = counter + 1
        if counter % 10 == 0:
            print(f"{counter} Tweets finished")
        try:
            if tweet["lang"] != current_language:
                current_language = tweet["lang"]
                nlp = spacy.load(language_models[current_language])
                stop_words = stopwords_lists[current_language]
            tweet["cleansed"] = preprocess(tweet["text"], nlp, stop_words, blacklist)
            markers_pin = extract_gpe(tweet["cleansed"], tweet["text"], tweet["created_at"], markers_pin, nlp, geolocator)
        except:
            pass
    return markers_pin