# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import time
import re
import json
import random
from twitter import *
import config


# loading the data
def LoadData(filename):

    df = pd.read_json(filename, orient='index', convert_dates=['created'])

    with open(filename) as json_data:
        dict = json.load(json_data)

    return df, dict


# connecting to twitter

twitter = Twitter(auth=OAuth(config.access_key,
                             config.access_secret,
                             config.consumer_key,
                             config.consumer_secret))

keys_to_keep = ['id',
                'name',
                'screen_name',
                'location',
                'description',
                'followers_count',
                'friends_count',
                'listed_count',
                'created_at',
                'favourites_count',
                'geo_enabled',
                'verified',
                'statuses_count',
                'lang']


def getUserData(screen_name):

    user_object = twitter.users.lookup(screen_name=screen_name)
    for user in user_object:
        if user['protected'] == False:
            user['description'] = user['description'].replace('\n', '').replace('\r', '')
    return {key: value for (key, value) in user.items() if key in keys_to_keep}


states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}
