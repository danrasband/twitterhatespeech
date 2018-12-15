# -*- coding: utf-8 -*-
import pandas as pd
import json
from twitter import *
import config

TWEETS_QUERY = "SELECT * FROM tweets WHERE language='en';"


# Load the data
from sqlalchemy import create_engine
db_conn = create_engine(config.POSTGRES_URL)

hate_tweets_df = pd.read_sql_query(TWEETS_QUERY, con=db_conn)
hate_tweets_df['retweet_count'] = pd.to_numeric(hate_tweets_df['retweet_count'])
hate_tweets_df['timestamp'] = pd.to_datetime(hate_tweets_df['timestamp'])

# create hate score (1 is added as original tweets have 0 retweets)
hate_tweets_df['hate_score'] = (1 + hate_tweets_df['retweet_count']) * hate_tweets_df['probability_hate']


# Chart #1: Time-series

# aggregate data by
by_hour_df = pd.DataFrame(hate_tweets_df['hate_score'].groupby([hate_tweets_df['timestamp'].dt.date.rename('day'), hate_tweets_df['timestamp'].dt.hour.rename('hour')]).sum())
by_hour_df.reset_index(inplace=True)
by_hour_df['day-hour'] = by_hour_df['day'].map(str) + " : " + by_hour_df['hour'].map(str)

# cutoff date for first retweet
start_date = pd.to_datetime("2018-12-07").date()
by_hour_df = by_hour_df[by_hour_df['day'] > start_date]

# Chart #2: Most common hashtags

hate_tweets_dict = hate_tweets_df[['text', 'hate_score']].to_dict(orient='index')

top_hash = {}
for tweet in hate_tweets_dict:
    words = hate_tweets_dict[tweet]['text'].split(" ")
    for word in words:
        if word and word[0] == "#":
            if word not in top_hash:
                # some tweets have link in them
                if word.find("http") > 0:
                    word = word[:word.find("http")]
                top_hash[word] = [hate_tweets_dict[tweet]['hate_score']]
            else:
                top_hash[word][0] += hate_tweets_dict[tweet]['hate_score']


top_hash_df = pd.DataFrame.from_dict(top_hash, orient='index')
top_hash_df.rename(columns={0: 'count'}, inplace=True)


# Chart #3: Haters

n_haters = 10

# selecting top users by their hate_score
haters_df = pd.DataFrame(hate_tweets_df['probability_hate']
                         .groupby(hate_tweets_df['screen_name'])
                         .mean())

top_haters_df = haters_df.sort_values(by='probability_hate', ascending=False)[:n_haters + 5]
top_haters_df.reset_index(inplace=True)

# connecting to twitter

twitter = Twitter(auth=OAuth(config.ACCESS_KEY,
                             config.ACCESS_SECRET,
                             config.CONSUMER_KEY,
                             config.CONSUMER_SECRET))

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


# pull follower counts for top users
top_hater_dict = {}
for hater in top_haters_df['screen_name']:
    try:
        top_hater_dict[hater] = getUserData(hater)
        top_hater_dict[hater]['probability_hate'] = top_haters_df['probability_hate'].loc[top_haters_df['screen_name'] == hater].values[0]
    except:
        top_hater_dict[hater] = {"name": "SUSPENDED", 'probability_hate': hater}


top_haters_df = pd.DataFrame.from_dict(top_hater_dict, orient="index")
top_haters_df = top_haters_df.loc[top_haters_df['name'] != "SUSPENDED"]
top_haters_df = top_haters_df.sort_values(by='probability_hate', ascending=False)[:n_haters]
top_haters_df = top_haters_df.sort_values(by='probability_hate', ascending=True)

# suspended = hater_df['screen_name'].loc[hater_df["name"] == "SUSPENDED"]

# Chart #4: Map
# source: https://plot.ly/python/choropleth-maps/

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

countries = {'AFG': 'Afghanistan',
             'ALB': 'Albania',
             'DZA': 'Algeria',
             'ASM': 'American Samoa',
             'AND': 'Andorra',
             'AGO': 'Angola',
             'AIA': 'Anguilla',
             'ATG': 'Antigua and Barbuda',
             'ARG': 'Argentina',
             'ARM': 'Armenia',
             'ABW': 'Aruba',
             'AUS': 'Australia',
             'AUT': 'Austria',
             'AZE': 'Azerbaijan',
             'BHM': 'Bahamas, The',
             'BHR': 'Bahrain',
             'BGD': 'Bangladesh',
             'BRB': 'Barbados',
             'BLR': 'Belarus',
             'BEL': 'Belgium',
             'BLZ': 'Belize',
             'BEN': 'Benin',
             'BMU': 'Bermuda',
             'BTN': 'Bhutan',
             'BOL': 'Bolivia',
             'BIH': 'Bosnia and Herzegovina',
             'BWA': 'Botswana',
             'BRA': 'Brazil',
             'VGB': 'British Virgin Islands',
             'BRN': 'Brunei',
             'BGR': 'Bulgaria',
             'BFA': 'Burkina Faso',
             'MMR': 'Burma',
             'BDI': 'Burundi',
             'CPV': 'Cabo Verde',
             'KHM': 'Cambodia',
             'CMR': 'Cameroon',
             'CAN': 'Canada',
             'CYM': 'Cayman Islands',
             'CAF': 'Central African Republic',
             'TCD': 'Chad',
             'CHL': 'Chile',
             'CHN': 'China',
             'COL': 'Colombia',
             'COM': 'Comoros',
             'COD': 'Congo, Democratic Republic of the',
             'COG': 'Congo, Republic of the',
             'COK': 'Cook Islands',
             'CRI': 'Costa Rica',
             'CIV': "Cote d'Ivoire",
             'HRV': 'Croatia',
             'CUB': 'Cuba',
             'CUW': 'Curacao',
             'CYP': 'Cyprus',
             'CZE': 'Czech Republic',
             'DNK': 'Denmark',
             'DJI': 'Djibouti',
             'DMA': 'Dominica',
             'DOM': 'Dominican Republic',
             'ECU': 'Ecuador',
             'EGY': 'Egypt',
             'SLV': 'El Salvador',
             'GNQ': 'Equatorial Guinea',
             'ERI': 'Eritrea',
             'EST': 'Estonia',
             'ETH': 'Ethiopia',
             'FLK': 'Falkland Islands (Islas Malvinas)',
             'FRO': 'Faroe Islands',
             'FJI': 'Fiji',
             'FIN': 'Finland',
             'FRA': 'France',
             'PYF': 'French Polynesia',
             'GAB': 'Gabon',
             'GMB': 'Gambia, The',
             'GEO': 'Georgia',
             'DEU': 'Germany',
             'GHA': 'Ghana',
             'GIB': 'Gibraltar',
             'GRC': 'Greece',
             'GRL': 'Greenland',
             'GRD': 'Grenada',
             'GUM': 'Guam',
             'GTM': 'Guatemala',
             'GGY': 'Guernsey',
             'GNB': 'Guinea-Bissau',
             'GIN': 'Guinea',
             'GUY': 'Guyana',
             'HTI': 'Haiti',
             'HND': 'Honduras',
             'HKG': 'Hong Kong',
             'HUN': 'Hungary',
             'ISL': 'Iceland',
             'IND': 'India',
             'IDN': 'Indonesia',
             'IRN': 'Iran',
             'IRQ': 'Iraq',
             'IRL': 'Ireland',
             'IMN': 'Isle of Man',
             'ISR': 'Israel',
             'ITA': 'Italy',
             'JAM': 'Jamaica',
             'JPN': 'Japan',
             'JEY': 'Jersey',
             'JOR': 'Jordan',
             'KAZ': 'Kazakhstan',
             'KEN': 'Kenya',
             'KIR': 'Kiribati',
             'PRK': 'Korea, North',
             'KOR': 'Korea, South',
             'KSV': 'Kosovo',
             'KWT': 'Kuwait',
             'KGZ': 'Kyrgyzstan',
             'LAO': 'Laos',
             'LVA': 'Latvia',
             'LBN': 'Lebanon',
             'LSO': 'Lesotho',
             'LBR': 'Liberia',
             'LBY': 'Libya',
             'LIE': 'Liechtenstein',
             'LTU': 'Lithuania',
             'LUX': 'Luxembourg',
             'MAC': 'Macau',
             'MKD': 'Macedonia',
             'MDG': 'Madagascar',
             'MWI': 'Malawi',
             'MYS': 'Malaysia',
             'MDV': 'Maldives',
             'MLI': 'Mali',
             'MLT': 'Malta',
             'MHL': 'Marshall Islands',
             'MRT': 'Mauritania',
             'MUS': 'Mauritius',
             'MEX': 'Mexico',
             'FSM': 'Micronesia, Federated States of',
             'MDA': 'Moldova',
             'MCO': 'Monaco',
             'MNG': 'Mongolia',
             'MNE': 'Montenegro',
             'MAR': 'Morocco',
             'MOZ': 'Mozambique',
             'NAM': 'Namibia',
             'NPL': 'Nepal',
             'NLD': 'Netherlands',
             'NCL': 'New Caledonia',
             'NZL': 'New Zealand',
             'NIC': 'Nicaragua',
             'NGA': 'Nigeria',
             'NER': 'Niger',
             'NIU': 'Niue',
             'MNP': 'Northern Mariana Islands',
             'NOR': 'Norway',
             'OMN': 'Oman',
             'PAK': 'Pakistan',
             'PLW': 'Palau',
             'PAN': 'Panama',
             'PNG': 'Papua New Guinea',
             'PRY': 'Paraguay',
             'PER': 'Peru',
             'PHL': 'Philippines',
             'POL': 'Poland',
             'PRT': 'Portugal',
             'PRI': 'Puerto Rico',
             'QAT': 'Qatar',
             'ROU': 'Romania',
             'RUS': 'Russia',
             'RWA': 'Rwanda',
             'KNA': 'Saint Kitts and Nevis',
             'LCA': 'Saint Lucia',
             'MAF': 'Saint Martin',
             'SPM': 'Saint Pierre and Miquelon',
             'VCT': 'Saint Vincent and the Grenadines',
             'WSM': 'Samoa',
             'SMR': 'San Marino',
             'STP': 'Sao Tome and Principe',
             'SAU': 'Saudi Arabia',
             'SEN': 'Senegal',
             'SRB': 'Serbia',
             'SYC': 'Seychelles',
             'SLE': 'Sierra Leone',
             'SGP': 'Singapore',
             'SXM': 'Sint Maarten',
             'SVK': 'Slovakia',
             'SVN': 'Slovenia',
             'SLB': 'Solomon Islands',
             'SOM': 'Somalia',
             'ZAF': 'South Africa',
             'SSD': 'South Sudan',
             'ESP': 'Spain',
             'LKA': 'Sri Lanka',
             'SDN': 'Sudan',
             'SUR': 'Suriname',
             'SWZ': 'Swaziland',
             'SWE': 'Sweden',
             'CHE': 'Switzerland',
             'SYR': 'Syria',
             'TWN': 'Taiwan',
             'TJK': 'Tajikistan',
             'TZA': 'Tanzania',
             'THA': 'Thailand',
             'TLS': 'Timor-Leste',
             'TGO': 'Togo',
             'TON': 'Tonga',
             'TTO': 'Trinidad and Tobago',
             'TUN': 'Tunisia',
             'TUR': 'Turkey',
             'TKM': 'Turkmenistan',
             'TUV': 'Tuvalu',
             'UGA': 'Uganda',
             'UKR': 'Ukraine',
             'ARE': 'United Arab Emirates',
             'GBR': 'United Kingdom',
             'USA': 'United States',
             'URY': 'Uruguay',
             'UZB': 'Uzbekistan',
             'VUT': 'Vanuatu',
             'VEN': 'Venezuela',
             'VNM': 'Vietnam',
             'WBG': 'West Bank',
             'YEM': 'Yemen',
             'ZMB': 'Zambia',
             'ZWE': 'Zimbabwe'}

location_df = hate_tweets_df[['location', 'probability_hate']].loc[hate_tweets_df['location'] != '(,)']

location_dict = location_df.to_dict(orient="index")

world_dict = {}
for record in location_dict:
    country = location_dict[record]['location'].split(",")[0][1:]
    if country == 'Brazil':
        country = 'Brasil'
    elif country == 'Bahamas':
        country = 'Bahamas, The'
    elif country == 'Italia':
        country = 'Italy'
    elif country == 'Republic of the Philippines':
        country = 'Philippines'
    elif country == 'Österreich':
        country = 'Austria'
    if country not in world_dict:
        world_dict[country] = {'hate_score': location_dict[record]['probability_hate'], 'count': 1}
    else:
        world_dict[country]['hate_score'] += location_dict[record]['probability_hate']
        world_dict[country]['count'] += 1

for country in world_dict:
    world_dict[country]['avg_score'] = world_dict[country]['hate_score'] / world_dict[country]['count']

world_df = pd.DataFrame.from_dict(world_dict, orient='index')
world_df.reset_index(inplace=True)
world_df.fillna(0, inplace=True)
world_df.rename(columns={'index': 'name'}, inplace=True)


countries_df = pd.DataFrame.from_dict(countries, orient='index').reset_index().set_index(0)\
                 .join(world_df.set_index('name')).reset_index()\
                 .rename(columns={'index': 'code', 0: 'name'})\
                 .fillna(0)
countries_df['level'] = 'World'

usa_df = location_df[['location', 'probability_hate']].loc[location_df['location'].str.contains('United States', case=False)]
usa_dict = usa_df.to_dict(orient="index")

states_dict = {state: {'hate_score': 0, 'count': 0} for state in states}
for record in usa_dict:
    place = usa_dict[record]['location'].split(",")[1][:-1]
    place_list = place.split()
    if len(place_list) == 2:
        if place_list[1] in states_dict:
            states_dict[place_list[1]]['hate_score'] += usa_dict[record]['probability_hate']
            states_dict[place_list[1]]['count'] += 1
        elif place_list[1] == 'USA':
            if place_list[0] in states.values():
                for abbr, full in states.items():
                    if full == place_list[0]:
                        states_dict[abbr]['hate_score'] += usa_dict[record]['probability_hate']
                        states_dict[abbr]['count'] += 1
        else:
            print(f"Invalid location: {usa_dict[record]}")

for state in states_dict:
    if states_dict[state]['count'] > 0:
        states_dict[state]['avg_score'] = states_dict[state]['hate_score'] / states_dict[state]['count']

states_df = pd.DataFrame.from_dict(states_dict, orient='index')
states_df.fillna(0, inplace=True)
states_df = states_df.join(pd.DataFrame.from_dict(states, orient='index')).reset_index().rename(columns={'index': 'code', 0: 'name'})
states_df['level'] = 'USA'

columns = ['level', 'code', 'name', 'count', 'hate_score', 'avg_score']

full_map_df = pd.concat([countries_df[columns], states_df[columns]])
