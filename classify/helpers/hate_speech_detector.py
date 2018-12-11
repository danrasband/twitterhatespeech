from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
from os.path import dirname, realpath
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from textstat.textstat import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class HateSpeechClassifier(object):
    '''This class takes some tweet text, preprocesses it to fill out its feature set,
    then classifies whether it is hate speech or not.'''
    
    def __init__(self):
        self.feature_preprocessor = FeaturePreprocessor()
        self.model = LogisticRegression(
            class_weight='balanced',
            penalty="l1",
            C=0.01,
        )
        return

    def fit(self, tweets, y):
        M = self.feature_preprocessor.fit_transform(tweets)
        X = pd.DataFrame(M)
        self.model.fit(X, y)
        return

    def predict(self, tweets):
        X = self.feature_preprocessor.transform(tweets)
        return self.model.predict(X)
    
    def predict_log_proba(self, tweets):
        X = self.feature_preprocessor.transform(tweets)
        return self.model.predict_log_proba(X)
    
    def predict_proba(self, tweets):
        X = self.feature_preprocessor.transform(tweets)
        return self.model.predict_proba(X)


class FeaturePreprocessor(object):
    def __init__(self):
        self.stopwords = self._stopwords()
        self.stemmer = PorterStemmer()
        self.tdidf_vectorizer = self._tdidf_vectorizer()
        self.pos_vectorizer = self._pos_vectorizer()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        return

    def fit_transform(self, tweets):
        tdidf = self.tdidf_vectorizer.fit_transform(tweets).toarray()
        tags = [self._tweet_tags(t) for t in tweets]
        pos = self.pos_vectorizer.fit_transform(pd.Series(tags)).toarray()
        other_features = self._featurize(tweets)
        return np.concatenate([tdidf, pos, other_features], axis=1)
    
    def transform(self, tweet_texts):
        tdidf = self.tdidf(tweet_texts)
        pos = self.pos(tweet_texts)
        other_features = self._featurize(tweet_texts)
        return np.concatenate([tdidf, pos, other_features], axis=1)
    
    def tdidf(self, tweets):
        return self.tdidf_vectorizer.transform(tweets).toarray()
    
    def pos(self, tweets):
        tags = [self._tweet_tags(t) for t in tweets]
        return self.pos_vectorizer.transform(pd.Series(tags)).toarray()

    def _tdidf_vectorizer(self):
        return TfidfVectorizer(
            tokenizer=self._tokenize,
            preprocessor=self._preprocess,
            ngram_range=(1, 3),
            stop_words=self.stopwords,
            use_idf=True,
            smooth_idf=False,
            norm=None,
            decode_error='replace',
            max_features=10000,
            min_df=5,
            max_df=0.75
        )

    def _pos_vectorizer(self):
        return TfidfVectorizer(
            tokenizer=None,
            lowercase=False,
            preprocessor=None,
            ngram_range=(1, 3),
            stop_words=None,
            use_idf=False,
            smooth_idf=False,
            norm=None,
            decode_error='replace',
            max_features=5000,
            min_df=5,
            max_df=0.75,
        )
    
    def _featurize(self, tweets):
        return np.array([self._get_other_features(t) for t in tweets])

    def _stopwords(self):
        words = stopwords.words("english")
        other_exclusions = ["#ff", "ff", "rt"]
        words.extend(other_exclusions)
        return words
    
    def _tweet_tags(self, tweet_text):
        tokens = self._basic_tokenize(self._preprocess(tweet_text))
        tags = pos_tag(tokens)
        tag_list = [x[1] for x in tags]
        return ' '.join(tag_list)
    
    def _preprocess(self, text):
        """
        Accepts a text string and replaces:
        1) urls with URLHERE
        2) lots of whitespace with one instance
        3) mentions with MENTIONHERE

        This allows us to get standardized counts of urls and mentions
        Without caring about specific people mentioned
        """
        space_pattern = '\s+'
        giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
            '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        mention_regex = '@[\w\-]+'
        parsed_text = re.sub(space_pattern, ' ', text)
        parsed_text = re.sub(giant_url_regex, '', parsed_text)
        parsed_text = re.sub(mention_regex, '', parsed_text)
        return parsed_text
    
    def _tokenize(self, text):
        '''Removes punctuation & excess whitespace, sets to lowercase,
        and stems tweets. Returns a list of stemmed tokens.'''
        text = ' '.join(re.split('[^a-zA-Z]*', text.lower())).strip()
        tokens = [self.stemmer.stem(t) for t in text.split()]
        return tokens

    def _basic_tokenize(self, text):
        """Same as tokenize but without the stemming"""
        text = ' '.join(re.split("[^a-zA-Z.,!?]*", text.lower())).strip()
        return text.split()
    
    def _get_other_features(self, tweet):
        """This function takes a string and returns a list of features.
        These include Sentiment scores, Text and Readability scores,
        as well as Twitter specific features"""
        sentiment = self.sentiment_analyzer.polarity_scores(tweet)

        words = self._preprocess(tweet) #Get text only

        syllables = textstat.syllable_count(words)
        num_chars = sum(len(w) for w in words)
        num_chars_total = len(tweet)
        num_terms = len(tweet.split())
        num_words = len(words.split())
        avg_syl = round(float((syllables+0.001))/float(num_words+0.001),4)
        num_unique_terms = len(set(words.split()))

        ###Modified FK grade, where avg words per sentence is just num words/1
        FKRA = round(float(0.39 * float(num_words)/1.0) + float(11.8 * avg_syl) - 15.59,1)
        ##Modified FRE score, where sentence fixed to 1
        FRE = round(206.835 - 1.015*(float(num_words)/1.0) - (84.6*float(avg_syl)),2)

        twitter_objs = self._count_twitter_objs(tweet)
        retweet = 0
        if "rt" in words:
            retweet = 1
        features = [FKRA, FRE,syllables, avg_syl, num_chars, num_chars_total, num_terms, num_words,
                    num_unique_terms, sentiment['neg'], sentiment['pos'], sentiment['neu'], sentiment['compound'],
                    twitter_objs[2], twitter_objs[1],
                    twitter_objs[0], retweet]
        return features

    def _count_twitter_objs(self, text_string):
        """
        Accepts a text string and replaces:
        1) urls with URLHERE
        2) lots of whitespace with one instance
        3) mentions with MENTIONHERE
        4) hashtags with HASHTAGHERE

        This allows us to get standardized counts of urls and mentions
        Without caring about specific people mentioned.

        Returns counts of urls, mentions, and hashtags.
        """
        space_pattern = '\s+'
        giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
            '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        mention_regex = '@[\w\-]+'
        hashtag_regex = '#[\w\-]+'
        parsed_text = re.sub(space_pattern, ' ', text_string)
        parsed_text = re.sub(giant_url_regex, 'URLHERE', parsed_text)
        parsed_text = re.sub(mention_regex, 'MENTIONHERE', parsed_text)
        parsed_text = re.sub(hashtag_regex, 'HASHTAGHERE', parsed_text)
        return (
            parsed_text.count('URLHERE'),
            parsed_text.count('MENTIONHERE'),
            parsed_text.count('HASHTAGHERE')
        )
