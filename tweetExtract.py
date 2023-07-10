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


!pip install snscrape
!pip install langdetect
import snscrape.modules.twitter as sntwitter
import pandas as pd
import warnings
from langdetect import detect

warnings.filterwarnings("ignore")

# Twitter API credentials
consumer_key = 'wAlRENtMC2xUl2oPOC1tnVO9f'
consumer_secret = 'znWgem5xGgCSknijSRmhyLTlEwoi56sKPv6yJaivLum3kRAW6N'
access_token = '1325044317212172289-krGskTYy1vJQBQEI3U7PE6MWuWW6O1'
access_token_secret = 'dKMDm9btO3YDF735DB7Jez18xDV8EFi7c3NnpMG8BO7yv'

date = datetime.datetime.now().date()
date = pd.to_datetime(date)


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
    json_data = resp.json()
    if 'data' in json_data:
        return json_data['data'][0]['conversation_id']
    else:
        return None


def getConversation(tweet_id):
    conversation = []

    # Get the conversation responses
    replies = tweepy.Cursor(api.search_tweets, q=f"to:{tweet_id}", tweet_mode='extended').items()

    # Add the responses to the list
    for reply in replies:
        if reply.in_reply_to_status_id_str == tweet_id:
            conversation.append(reply)

    # Check if the tweet has a conversation
    if conversation:
        # Get the tweet initial
        tweet = api.get_status(tweet_id, tweet_mode='extended')
        conversation.insert(0, tweet)

    return conversation


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
limit = 300

keywords = ["drone commercial", "capacité drone", "sécurité drone"]
i = 0
for keyword in keywords:
    tweets = tweepy.Cursor(api.search_tweets, q=keyword, count=10, tweet_mode='extended', lang="fr").items(limit)
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
        j = 0
        for tweet in tweets:
            convId = getConversationId(tweet.id)
            tweetData = {
                "id": tweet.id,
                "conversation_id": convId,
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

            tweets_df = pd.DataFrame()  # Dataframe pour stocker les tweets
            conversations_df = pd.DataFrame(columns=["tweet_id", "tweet"])
            # get the tweet conversation
            conversation = getConversation(tweet.id)
            if conversation is not None and len(conversation) > 0:
                # Browsing through the tweets of the conversation
                for conv_tweet in conversation:
                    # add the tweet to the conversation tweet
                    conversation_data = {
                        "conversation_id": convId,
                        "tweet_id": conv_tweet.id,
                        "tweet": conv_tweet.full_text
                    }
                    conversations_df = conversations_df.append(conversation_data, ignore_index=True)
                conversations_df.to_csv("tweets" + i + "conversations" + j + ".csv")
                i += 1

            time.sleep(3)
        # save the tweets in a csv file
        tweetsDf.to_csv("tweetsExtracted" + str(i) + ".csv", index=True)
        print(i)
        tweetsDf.astype(str)

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=UserWarning, module="snscrape.modules.twitter")
tweets = []
limit = 300
query = " choose my keyword"

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    warnings.filterwarnings("ignore")
    # print(vars(tweet))
    # break
    if detect(tweet.content) == 'fr':
      if len(tweets) == limit:
          break
      else:
          tweets.append([
              tweet.id,
              tweet.conversationId,
              tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
              tweet.date.strftime('%Y-%m-%d'),
              tweet.date.strftime('%H:%M:%S'),
              tweet.date.strftime('%Z'),
              tweet.user.id,
              tweet.user.username,
              tweet.place,
              tweet.content,
              "",
              "",
              tweet.lang,
              tweet.source,
              tweet.replyCount,
              tweet.retweetCount,
              tweet.likeCount,
             ])

d = pd.DataFrame(tweets, columns=['id','conversation_id','created_at','date', 'time','timezone','user_id','username','place','tweet','labelAsma','labelGPT','language','source','reply_count','retweet','like_count'])
#save to csv
#d.to_csv('tweetHash1.csv')




