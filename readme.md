# Real Time Monitoring of Hate Speech on Twitter

## Final Project for "W251. Scaling Up! Real Big Data"
#### Master of Information and Data Science at UC Berkeley School of Information

&nbsp;

### Dan Rasband and Yulia Zamriy
#### December 17th, 2018

&nbsp;

### Introduction

Social platforms have become our everyday reality. We use them for connecting with friends, checking news, sharing content. They cross boundaries and open doors; they level the playing field. But as much as they are praised for being a platform for equality and empowerment, they also bear responsibility for uncovering and fueling hate in cyberspace, which frequently leads to violence in the physical world.

One of the main issues that prohibits social networks from creating guidelines on communication decency is the lack of legislation that defines hate speech. But beyond legislation, how do we define hate speech? How do we create an objective definition beyond personal opinions? And how do we not violate the First Amendment?

Many attempts have been made to use machine learning in classifying hate speech: [Waseem](http://aclweb.org/anthology/N16-2013), [Gröndahl](https://arxiv.org/abs/1808.09115), [Davidson](https://arxiv.org/abs/1703.04009), [Malmasi](https://arxiv.org/abs/1712.06427), [Zhang](https://arxiv.org/abs/1803.03662) and many others. But most of them still live in the research papers of their original authors. Companies like Twitter also work proactively to identify and remove tweets and accounts that violate their ever changing policies. And yet, we still have no clear visibility of how deep the issue is and how well social media companies are dealing with it.

Our main goal for this project is to provide the public with open and simple visualizations about the proliferation of hate speech on Twitter using (behind the scenes but open to everyone to explore) machine learning algorithms. Our dashboard answers questions such as:

- How bad is the hate speech situation now on Twitter?
- What are the hashtags used by people promoting hate speech?
- Who are the worst offenders and how visible they are in the network?
- What are the hotspots of hate speech across the globe?


### Background

The First Amendment to the US Constitution, ratified on December 15, 1791, states that:
> **Congress shall make no law** respecting an establishment of religion, or prohibiting the free exercise thereof; or **abridging the freedom of speech, or of the press**; or the right of the people peaceably to assemble, and to petition the Government for a redress of grievances.

The amendment was designed to protect our ability to express our opinions through speech, actions, written text, appearance and other forms of expression. It's at the core of the US democracy.

We are all well aware of the ongoing debate about the definition and scope of free speech. There are a lot of opinions, and frequently the loudest, but not necessarily the most objective, stand out. However, as data scientists we firmly believe that on the aggregate level, when the opinions are measured and averaged across cultures, societies, and continents, the definition can become more objective and actually implementable. That's the power of machine learning algorithms applied to labeled data.

After researching the above mentioned research papers on hate speech identification, we selected ["Automated Hate Speech Detection and the Problem of Offensive Language"](https://github.com/t-davidson/hate-speech-and-offensive-language) by [Davidson](https://arxiv.org/abs/1703.04009) for our baseline model because:

- It contains the underlying data with tweets classified as `hate speech`, `offensive language` and `neither` that we can use to retrain the model
- We were able to successfully replicate the model based on their data and code
- The authors achieved reasonable accuracy
- The output contains probabilities that we can use to assess the severity of the problem
- This research is relatively recent

An additional source of inspiration was the [Extreme Right Dashoboard](https://extremeright.thinkprogress.org/) by [ThinkProgress](https://thinkprogress.org/). However, their analysis is focused on scraping the data on a short list of users that have certain key words in their profiles or names (for example, `alt-right`, `red-pill`, `fashy`, `14/88`, `identitarian`, `nationalist`). The issue with this approach is that hate speech is not limited to self-proclaimed nationalists. Moreover, users describing themselves as far right do not necessarily use hate speech, at least not often. The counter argument to that criticism could be that a lot of hate speech can be implied in otherwise innocent words. Our goal is to use an algorithm that can objectively detect elements of hate speech, and no well-researched algorithm so far has been able to decipher implied meanings (at least to our best knowledge).

### The Data

For model training we used labeled [data](https://github.com/t-davidson/hate-speech-and-offensive-language/tree/master/data) from Davidson that contains around 24k tweets that were classified as one of "hate speech" (0), "offensive language" (1), and "neither" (2). The labels were obtained through CrowdFlower (now [Figure Eight](https://www.figure-eight.com/)); the original researchers kept the tweets that were labeled by at least 3 people.

<div align="center">
  <img
    src="images/tweet_class_histogram.png?raw=true"
    alt="Tweet Class Histogram"
    title="Tweet Classes Histogram - Not much hate speech to train on, but tweets seem to be mostly offensive in general..."
  >
</div>

We launched data collection on Wednesday, 12 December, 2018 at 12:27am MST. As of December 15th, 2018 at approximately 5pm MST, we had collected 9,145,934 tweets, and out of those 323,372 (approximately 3.5%) were classified as hate speech.

### Model

The model (again, taken from [Davidson](https://github.com/t-davidson/hate-speech-and-offensive-language/tree/master/data)) uses a feature preprocessing pipeline and logistic regression. The feature vectorization pipeline is discussed in more detail below.

The model was initially trained on a training set of 22,304 labeled tweets and a test set of 2,479. Hyperparameter optimization was done using a gridsearch method, and a logistic regression model was chosen, using an inverse regularization of 0.01, an L1 penalty, and balanced class weights.

For this project, we rebuilt and reproduced the model in a way that would support pickling the model for productionalization. In our training step, we opted to use the full labeled data set because there was no need at this point to do hyperparameter optimization. Training on the whole set seems to have slightly decreased its hate speech recall, but we believe the reported performance is more realistic now.

#### Model: Feature Vectorization

Since tweets can contain any number of words and characters (including emojis and other unicode characters) up to 280 characters, a methodology is required to convert those tweets into a vector of numerical features for training and inference. Davidson implemented a complex set of features for each tweet, including some preprocessing steps such as tokenizing, lower-casing, and stemming. The main aspects of the feature pipeline, however, included the following:

- A __word TF-IDF__ (term frequency-inverse document frequency) vector, using 1- to 3-grams
- A (part of speech) __POS TF-IDF__ vector, using 1- to 3-grams
- A vector of other features:
    - __Sentiment analysis__ (intensity), using the VADER Sentiment Analysis tool
    - __Word feature counts__ (words, syllables, characters, etc.)
    - __Readability scores__ FKRA and FKE
    - __Twitter Object counts__ (URLs, mentions, hashtags)
    - __Retweet boolean__ (whether the tweet was a retweet)

These vectors were concatenated to produce 4023 features for each tweet. This pipeline can be better viewed in the diagram below:

<div align="center">
  <img
    src="diagrams/FeatureVectorization.png?raw=true"
    alt="Feature Vectorization Pipeline Diagram"
    title="Feature Vectorization Pipeline"
  >
</div>

#### Model: Results

Our reproduction of the model produced similar results to Davidson's:

```
              precision    recall  f1-score   support

           0       0.40      0.45      0.42      1430
           1       0.94      0.87      0.90     19190
           2       0.66      0.83      0.74      4163

   micro avg       0.84      0.84      0.84     24783
   macro avg       0.66      0.72      0.69     24783
weighted avg       0.86      0.84      0.85     24783
```

As can be seen, the recall for tweets containing hate speech is approximately 45%, with an overall F1 score of 85%. The support for hate speech examples is relatively low, which may have contributed to the difficulty in training for a better recall rate. We can see in the confusion matrix below that the model classifies hate speech as offensive 37% of the time and as neither 17% of the time:

<div align="center">
  <img
    src="images/confusion_matrix.png?raw=true"
    alt="Confusion Matrix Plot"
    title="Confusion Matrix. Need to catch more of the hate speech."
  >
</div>

This is certainly not ideal, but it is a reasonable start, given the data provided and the difficulty of the task.

### Infrastructure

In order to stream and process tweets continuously, we have set up an easily-scalable architecture including nodes that run Spark for streaming, Kafka for storing tweets, a Python script for classifying tweets, a Postgres database for aggregating statistics, and a Flask server running Dash for visualizing the data. A diagram of the infrastructure is shown below:

<div align="center">
  <img
    src="diagrams/InfrastructureDiagram.png?raw=true"
    alt="Infrastructure Diagram"
    title="System Infrastructure"
  >
</div>

Each piece of the infrastructure is easily scalable. If we were to start streaming all tweets, for example, we could add more Spark nodes, more Kafka nodes, and more processing nodes to handle the larger amount of data being streamed in. Both Kafka (along with Zookeeper) and the Python script are run on Docker containers, so they could also potentially be deployed to a Kubernetes cluster without much trouble. Kafka allows the Python Kafka consumer to work as a group to retrieve tweets from Kafka.

### Dashboard

The result of our work is presented in almost real time (currently it's refreshed every five minutes) on [https://twitterhatespeech.org/](https://twitterhatespeech.org/). The dashboard was created using [Dash by plotly](https://plot.ly/products/dash/). It displays the data for the last 24 hours from around the world (for English-language tweets).

Two main metrics used are as following:

- Hate Score: tweet's probability of hate speech
- Total Hate Score: tweet's probability of hate speech multiplied by the total number of retweets

The Dashboard consists of five sections:

- Section 1: The Header
    + Update time (UTC)
    + Number of English-language tweets classified as hate speech in the last 24 hours.

<div align="center">
  <img
    src="images/header.png?raw=true"
    alt="Dashboard header"
    title="Dashboard header"
  >
</div>


- Section 2: Hourly Activity
    + Aggregated total hate score by hour

<div align="center">
  <img
    src="images/timeseries.png?raw=true"
    alt="Time Series Graph"
    title="Time Series"
  >
</div>

- Section 3: Most Common Hashtags
    + 10 most common hashtags as determined by their frequency of occurrence weighted by hate score

<div align="center">
  <img
    src="images/hashtags.png?raw=true"
    alt="Hashtags Graph"
    title="Hashtags"
  >
</div>

- Section 4: Top 10 Users Promoting Hate speech
    + Rated by the average hate score of their tweets
    + Also included: their most recent followers count as the influence indicator within the network

<div align="center">
  <img
    src="images/top10users.png?raw=true"
    alt="Top10Users Graph"
    alt="Top 10 Users">
</div>

- Section 5: Hate Speech geographical hot spots
    + Average hate score by country (Global) or state (US only)
    + The global map is sparsely populated mostly due to English language restriction, not because hate speech is not common there

<div align="center">
  <img
    src="images/usa.png?raw=true"
    alt="USA Graph"
    title="USA"
  >
</div>

<div align="center">
  <img
    src="images/global.png?raw=true"
    alt="Global Graph"
    title="Global"
  >
</div>

### Replication

All the scripts necessary to replicate our work are provided in this repo:

- [streaming](https://github.com/YuliaZamriy/W251-final-project/tree/master/streaming) folder contains all the scripts for collecting streaming data from Twitter, including how to set up `kafka` and run `scala` scripts
- [classify](https://github.com/YuliaZamriy/W251-final-project/tree/master/classify) folder contains all the scripts for running the model including the data used in the original research
- [analyze](https://github.com/YuliaZamriy/W251-final-project/tree/master/analyze) folder contains all the scripts necessary for populating and running the dashboard
    + [data](https://github.com/YuliaZamriy/W251-final-project/tree/master/analyze/data) sub-folder contains a small portion of data collected from Twitter before classification

### Future Work

This project is only the first step in analyzing hate speech in real time. There are many directions that we can take, but the most relevant next steps can be broken down into two categories:

1. *Framework: Improving hate speech classifier*
    - As of this moment we have implemented only one of the existing models. There are quite a few others we could test and possibly build an ensemble solution. Another alternative would be to leverage [Perspective API](https://github.com/conversationai/perspectiveapi) that identifies `toxic` speech
    - One of the keys to building a robust classifier is quality labels. Hence, extending training dataset could help us improve the model. One of the most common crowd sourcing platforms is [Amazon Mechanical Turk](https://www.mturk.com/,) and we could use it to label new data
    - Add granularity to classification of hate speech (misogynist, homophobic, racist, etc.)
2. *Dashboard: Adding more context to the analysis*
    - Combine hate speech locations with reports of crime
    - Add the option to extend the timeline beyond 24 hours
    - Introduce more languages
    - Ability to export the underlying data (currently it's possible only by clicking on `Edit in Chart Studio` button associated with each chart)
    - Add a live feed of hate speech along with relevant news feeds
