#!/usr/bin/env python3.6

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

keys_to_keep = ['id', 'id_str', 'name', 'screen_name', 'location', 'description',
                'followers_count', 'friends_count', 'listed_count', 'created_at', 'favourites_count',
                'geo_enabled', 'verified', 'statuses_count', 'lang']

today_dt = datetime.today()

with open('user_names_separate.txt') as f:
    new_users = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
new_users = [x.strip() for x in new_users]

with open('user_names.txt') as f:
    pulled_users = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
all_users = [x.strip() for x in pulled_users]


def cleanUser(user):
    if user['screen_name'] not in all_users:
        if user['protected'] == False and user['lang'] == 'en':
            last_status_dt = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S %z %Y')
            last_status_dt = last_status_dt.replace(tzinfo=None)
            diff_dt = today_dt - last_status_dt
            if diff_dt.days < 180:
                all_users.append(user)
                return {key: value for (key, value) in user.items() if key in keys_to_keep}


new_users_full = []
for n in new_users:
    user = twitter.users.lookup(screen_name=n)
    clean_user = cleanUser(user[0])
    if clean_user:
        new_users_full.append(clean_user)

filename = './data/user_list_separate.txt'
orig_stdout = sys.stdout
f = open(filename, 'w')
sys.stdout = f

for user in new_users_full:
    print(*list(user.values()), sep="\t")

sys.stdout = orig_stdout
f.close()
