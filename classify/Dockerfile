FROM python:3.7.1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader averaged_perceptron_tagger

COPY HateSpeechClassifier.20181211-014208.pkl .
COPY process_tweets.py .
RUN mkdir helpers
COPY helpers/* helpers/

CMD [ "python", "./process_tweets.py" ]
