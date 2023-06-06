# from google.cloud import translate
# create an instance
# translate_client = translate.TranslationServiceClient()
# srcLanguage="fr"
# targetLanguage = "en"
# parent = translate_client.location_path("####id_google_cloud", "global")
import tweepy
from tweepy import *
import pandas as pd
import csv
import re
import string
import preprocessor as p
import csv
import time
from datetime import datetime, timedelta
import datetime
import base64
import requests
import warnings

warnings.filterwarnings("ignore")

# Twitter API credentials
consumer_key = 'wAlRENtMC2xUl2oPOC1tnVO9f'
consumer_secret = 'znWgem5xGgCSknijSRmhyLTlEwoi56sKPv6yJaivLum3kRAW6N'
access_token = '1325044317212172289-krGskTYy1vJQBQEI3U7PE6MWuWW6O1'
access_token_secret = 'dKMDm9btO3YDF735DB7Jez18xDV8EFi7c3NnpMG8BO7yv'

date = datetime.datetime.now().date()
date = pd.to_datetime(date)

keyword = "drone commercial OR drones commerciaux OR capacité drone OR sécurité drone"


def get_bearer_header():
    uri_token_endpoint = 'https://api.twitter.com/oauth2/token'
    key_secret = f"{consumer_key}:{consumer_secret}".encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret)
    b64_encoded_key = b64_encoded_key.decode('ascii')

    auth_headers = {
        'Authorization': 'Basic {}'.format(b64_encoded_key),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    auth_data = {
        'grant_type': 'client_credentials'
    }

    auth_resp = requests.post(uri_token_endpoint, headers=auth_headers, data=auth_data)
    bearer_token = auth_resp.json()['access_token']

    bearer_header = {
        'Accept-Encoding': 'gzip',
        'Authorization': 'Bearer {}'.format(bearer_token),
        'oauth_consumer_key': consumer_key
    }
    return bearer_header


def getConversationId(id):
    uri = 'https://api.twitter.com/2/tweets?'

    params = {
        'ids': id,
        'tweet.fields': 'conversation_id'
    }

    bearer_header = get_bearer_header()
    resp = requests.get(uri, headers=bearer_header, params=params)
    return resp.json()['data'][0]['conversation_id']


# Authenticate with Twitter API

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
limit = 300
tweets = tweepy.Cursor(api.search_tweets, q=keyword, count=10, tweet_mode='extended').items(limit)
if auth.access_token is None:
    print("Authentication failed.")
else:
    print("Authentication successful.")
    tweetsDf = pd.DataFrame(
        columns=
        ["id", "conversation_id", "created_at", "date", "time", "timezone", "user_id", "username", "name", "place",
         "tweet", "language", "mentions", "urls", "photos", "replies_count", "retweets_count", "likes_count",
         "hashtags", "cashtags", "link", "retweet", "quote_url", "video", "thumbnail", "near", "geo", "source",
         "user_rt_id", "user_rt", "retweet_id", "reply_to", "retweet_date", "translate", "trans_src", "trans_dest"]
    )
    i = 0
    for tweet in tweets:
        tweetData = {
            "id": tweet.id,
            "conversation_id": getConversationId(tweet.id),
            "created_at": tweet.created_at,
            "date": tweet.created_at.date(),
            "time": tweet.created_at.time(),
            "timezone": tweet.created_at.strftime("%Z"),
            "user_id": tweet.user.id,
            "username": tweet.user.screen_name,
            "name": tweet.user.name,
            "place": tweet.place.full_name if tweet.place else None,
            "tweet": tweet.full_text,
            "language": tweet.lang,
            "mentions": [mention["screen_name"] for mention in tweet.entities["user_mentions"]],
            "urls": [url["expanded_url"] for url in tweet.entities["urls"]],
            "photos": [media["media_url_https"] for media in tweet.entities.get("media", []) if
                       media["type"] == "photo"],
            # "replies_count": tweet.reply_count,
            "retweets_count": tweet.retweet_count,
            "likes_count": tweet.favorite_count,
            "hashtags": [hashtag["text"] for hashtag in tweet.entities["hashtags"]],
            "cashtags": [cashtag["text"] for cashtag in tweet.entities["symbols"]],
            "link": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
            "retweet": tweet.retweeted,
            # "quote_url": tweet.quoted_status_permalink["expanded"],
            "video": tweet.entities.get("media", [{}])[0].get("video_info", {}).get("variants", [{}])[0].get("url"),
            "thumbnail": tweet.entities.get("media", [{}])[0].get("media_url_https"),
            "near": tweet.geo["coordinates"] if tweet.geo else None,
            "geo": tweet.place.bounding_box.coordinates if tweet.place else None,
            "source": tweet.source,
            "user_rt_id": tweet.user.id_str,
            "user_rt": tweet.user.screen_name,
            "retweet_id": tweet.retweeted_status.id_str if hasattr(tweet, "retweeted_status") else None,
            "reply_to": tweet.in_reply_to_status_id_str,
            "retweet_date": tweet.retweeted_status.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(tweet, "retweeted_status")
            else None,
            #   "translate" = translate_client.translate_text(
            #   request={
            #       "parent": parent,
            #       "contents": [tweet.full_text],
            #       "source_language":srcLanguage,
            #       "target_language_code": targetLanguage,
            #   }
            # ).translations[0].translated_text

        }
        tweetsDf = tweetsDf.append(tweetData, ignore_index=True)
        time.sleep(3)
    # save the tweets in a csv file
    tweetsDf.to_csv("tweets.csv", index=True)








