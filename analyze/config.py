# This file loads all the credentials from the .env file.

from dotenv import load_dotenv
from os import getenv

load_dotenv(verbose=True, dotenv_path='.env')

# Twitter Credentials
CONSUMER_KEY = getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = getenv('TWITTER_CONSUMER_SECRET')
ACCESS_KEY = getenv('TWITTER_ACCESS_TOKEN')
ACCESS_SECRET = getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Postgres Database
POSTGRES_URL = getenv('POSTGRES_URL')
