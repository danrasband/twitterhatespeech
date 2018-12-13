# Process tweets continuously as they are inserted into Kafka.

# Imports
## Data Wrangling
import pandas as pd
import numpy as np

## Kafka
from confluent_kafka import Consumer, KafkaError, KafkaException

## Utils
import logging
from os import getenv
import re
import sys
from time import sleep

## Data & Models
import pickle
from pony import orm
# ! pip install psycopg2

# Globals

## Kafka Config
TOPICS = getenv('KAFKA_TOPIC').split(',')
TWEETS_INTERVAL = 100
SLEEP_INTERVAL = 10
BOOTSTRAP_SERVERS = getenv('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_GROUP = getenv('KAFKA_GROUP')

## Postgres Config
DB = orm.Database()

class DBTweet(DB.Entity):
    _table_ = "tweets"
    id = orm.PrimaryKey(int, auto=True, size=64)
    tweet_id = orm.Required(int, size=64)
    screen_name = orm.Required(str)
    timestamp = orm.Required(str)
    text = orm.Required(str)
    is_truncated = orm.Required(bool)
    is_retweet = orm.Required(bool)
    retweet_count = orm.Required(int)
    favorite_count = orm.Required(int)
    is_possibly_sensitive = orm.Required(bool)
    language = orm.Optional(str)
    location = orm.Required(str)
    vocab_match_count = orm.Required(int)
    kafka_timestamp = orm.Required(int, size=64)
    probability_hate = orm.Required(float)
    probability_offensive = orm.Required(float)
    probability_neither = orm.Required(float)
    label = orm.Required(int)

DB.bind(
    provider='postgres',
    user=getenv('DB_USER'),
    password=getenv('DB_PASS'),
    host=getenv('DB_HOST'),
    database=getenv('DB_NAME'),
)
DB.generate_mapping(create_tables=True)


## Regex for parsing tweets from Kafka
TUPLE_REGEX = re.compile(r'''
    ^\(
        (?P<tweet_id>[^,]+),
        (?P<screen_name>[^,]+),
        (?P<timestamp>[^,]+),
        (?P<text>.*),
        (?P<is_truncated>[^,]+),
        (?P<is_retweet>[^,]+),
        (?P<retweet_count>[^,]+),
        (?P<favorite_count>[^,]+),
        (?P<is_possibly_sensitive>[^,]+),
        (?P<language>[^,]+),
        (?P<location>\(.+\)),
        (?P<vocab_match_count>[^,]+)
    \)$
''', re.X)


class TweetProcessor(object):
    '''Process tweets from Kafka and insert tweets with potential hate speech
    into a Postgres database.'''

    def __init__(self):
        '''Load up the Hate Speech Classifier and set up logging.'''
        with open('HateSpeechClassifier.20181211-014208.pkl', 'rb') as file:
            self.model = pickle.load(file)

        # Set up logger
        logger = logging.getLogger('consumer')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)
        self.logger = logger
        return

    def stream_kafka(self, topics=TOPICS, tweets_per_interval=TWEETS_INTERVAL):
        '''Stream from the specified topics in Kafka.'''
        try:
            # Instantiate Kafka consumer
            consumer = Consumer({
                'bootstrap.servers': BOOTSTRAP_SERVERS,
                'group.id': KAFKA_GROUP,
                'auto.offset.reset': 'earliest',
                'session.timeout.ms': 6000,
            }, logger=self.logger)
            consumer.subscribe(topics)
            self._loop(consumer, tweets_per_interval)
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            # Close down consumer to commit final offsets.
            consumer.close()

    def process_tweets(self, tweets):
        '''Classify tweets and send the hateful once to Postgres.'''
        tweets_df = pd.DataFrame.from_records(tweets)
        probability_columns = [
            'probability_hate',
            'probability_offensive',
            'probability_neither',
        ]
        probabilities = self.model.predict_proba(tweets_df.text)
        labels = np.argmax(probabilities, axis=1)

        probabilities_df = pd.DataFrame(
            probabilities,
            columns=probability_columns,
        )
        probabilities_df['label'] = labels

        tweets_df = pd.concat([tweets_df, probabilities_df], axis=1)

        hate_tweets = tweets_df[tweets_df.label == 0]
        self._insert_tweets(hate_tweets)
        return


    def _loop(self, consumer, tweets_per_interval=TWEETS_INTERVAL):
        '''Loop over Kafka consumer indefinitely.'''
        tweets = []
        while True:
            if len(tweets) >= tweets_per_interval:
                self.process_tweets(tweets)
                tweets = []

            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                # Error or event
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d, sleeping before trying again...\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                    sleep(SLEEP_INTERVAL)
                else:
                    # Error
                    raise KafkaException(msg.error())
            else:
                tweet = self._parse_tweet_tuple(msg.value().decode('utf-8'))
                tweet['kafka_timestamp'] = msg.timestamp()[1]
                tweets.append(tweet)

        if len(tweets) > 0:
            self.process_tweets(tweets)

        return

    def _parse_tweet_tuple(self, tuple_str):
        '''Turn a stringified tuple into a dict.'''
        match = TUPLE_REGEX.match(tuple_str)
        boolean_columns = [
            'is_truncated',
            'is_retweet',
            'is_possibly_sensitive',
        ]
        if match is not None:
            tweet = match.groupdict()
            for column in boolean_columns:
                tweet[column] = self._convert_bool(tweet[column])
            return tweet
        else:
            raise Error('Can\'t parse: {}'.format(tuple_str))

    def _convert_bool(self, value):
        if value == '1':
            return True
        return False

    @orm.db_session
    def _insert_tweets(self, tweets_df):
        '''Insert tweets into the db.'''
        _tweets_to_insert = [DBTweet(**tweet) for _, tweet in tweets_df.iterrows()]
        orm.commit()
        return


if __name__ == "__main__":
    TweetProcessor().stream_kafka()
