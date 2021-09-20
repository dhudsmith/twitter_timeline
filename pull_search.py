"""
This script handles the polling of user data using the tweets api. API reference:
https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-by
"""
import os
from tweepy.client import Client
import yaml
import pprint
from utils.config_schema import TwitterPullConfig
from utils.tweet_search import TweetSearch
import pandas as pd

def pull_search(config: TwitterPullConfig, client: Client, query: str,
    max_response: int = 100,
    start_time: str = None, 
    end_time: str = None):

    # set up the timeline
    tweet_search = TweetSearch(client, config.twitter.query_params)

    try:
        tweet_search.pull(query, output_dir=str(config.local.output_dir),
            start_time = start_time, end_time = end_time,
            max_results = max_response, batch_size  = config.twitter.account.tweets_per_query)
    except Exception as e:
        print(f"Failed to pull tweets for query. Error: ", e)