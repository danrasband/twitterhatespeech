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
unique_users = []


def cleanUsers(result):
    result_clean = []
    for user in result:
        if user not in unique_users:
            if user['protected'] == False and user['lang'] == 'en' and 'status' in user:
                last_status_dt = datetime.strptime(user['status']['created_at'], '%a %b %d %H:%M:%S %z %Y')
                last_status_dt = last_status_dt.replace(tzinfo=None)
                diff_dt = today_dt - last_status_dt
                if diff_dt.days < 60 and user['followers_count'] > 100:
                    unique_users.append(user)
                    user['description'] = user['description'].replace('\n', '').replace('\r', '')
                    user_clean = {key: value for (key, value) in user.items() if key in keys_to_keep}
                    result_clean.append(user_clean)
    return result_clean


for j in sys.stdin:

    filename = './data/user_list_' + j.replace(' ', '').rstrip() + '.txt'
    orig_stdout = sys.stdout
    f = open(filename, 'w')
    sys.stdout = f

    for i in range(50):
        all_users = twitter.users.search(q=j, page=i, count=20)
        filtered_users = cleanUsers(all_users)
        for user in filtered_users:
            print(*list(user.values()), sep="\t")

    sys.stdout = orig_stdout
    f.close()


# users = []
# for j in search_list:
#     for i in range(2):
#         all_users = twitter.users.search(q=j, page=i, count=20)
#         filtered_users = cleanUsers(all_users)
#         users += filtered_users

#     filename = './data/user_list' + j.replace(' ', '') + '.json'

#     with open(filename, 'w') as outfile:
#         json.dump(users, outfile)
