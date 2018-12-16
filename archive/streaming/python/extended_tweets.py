#!/usr/bin/env python3

"""Source of inspiration: https://github.com/ideoforms/python-twitter-examples/blob/master/twitter-user-search.py"""

from twitter import *
import json
from datetime import datetime

import sys
sys.path.append(".")
import config

twitter = Twitter(auth=OAuth(config.access_key,
                             config.access_secret,
                             config.consumer_key,
                             config.consumer_secret))

tweet = twitter.statuses.show(id=1067133134452473858, tweet_mode='extended')

for i in tweet:
    print(f"{i}: {tweet[i]}")

print(tweet)
