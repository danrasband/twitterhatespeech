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

- It contains the underlying data with tweets classified as `hate speech`, `offensive language` and `other` that we can use to retrain the model
- We were able to successfully replicate the model based on their data and code
- The authors achieved reasonable accuracy
- The output contains probabilities that we can use to assess the severity of the problem
- This research is relatively recent

An additional source of inspiration was the [Extreme Right Dashoboard](https://extremeright.thinkprogress.org/) by [ThinkProgress](https://thinkprogress.org/). However, their analysis is focused on scraping the data on a short list of users that have certain key words in their profiles or names (for example, `alt-right`, `red-pill`, `fashy`, `14/88`, `identitarian`, `nationalist`). The issue with this approach is that hate speech is not limited to self-proclaimed nationalists. Moreover, users describing themselves as far right do not necessarily use hate speech, at least not often. The counter argument to that criticism could be that a lot of hate speech can be implied in otherwise innocent words. Our goal is to use an algorithm that can objectively detect elements of hate speech, and no well-researched algorithm so far has been able to decipher implied meanings (at least to our best knowledge).

### The Data

For model training we used labeled [data](https://github.com/t-davidson/hate-speech-and-offensive-language/tree/master/data) from Davidson that contains around 24k tweets that were classified as hate speech (0), offensive language (1) and neither (2). The labels were obtained through CrowdFlower (now [Figure Eight](https://www.figure-eight.com/)); the original researchers kept the tweets that were labeled by at least 3 people.

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/hist_012.png?raw=true" width="350" height="250" title="Histogram of Target">
</p>

We launched data collection on Wednesday, 12 December, 2018 at 12:27am MST. As of December 15th, 2018 at approximately 5pm MST, we had collected 9,145,934 tweets, and out of those 323,372 (approximately 3.5%) were classified as hate speech.

### Model

**TODO: very briefly describe the model and list most important features and model performance**


### Infrasturcture

&nbsp;

### Dashboard

The result of our work is presented in real time on [https://twitterhatespeech.org/](https://twitterhatespeech.org/). The dashboard was created using [Dash by plotly](https://plot.ly/products/dash/). It displays the data for the last 24 hours from around the world (for English-language tweets). 

Two main metrics used are as following:

- Hate Score: tweet's probability of hate speech 
- Total Hate Score: tweet's probability of hate speech multiplied by the total number of retweets

The Dashboard consists of five sections:

- Section 1: The Header
    + Update time (UTC)
    + Number of English-language tweets classified as hate speech in the last 24 hours (based on the **TODO: what is the probability for the tweet to be calssified as hate speech?** cutoff point)

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/header.png?raw=true" title="Dashboard header">
</p>


- Section 2: Hourly Activity
    + Aggregated total hate score by hour

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/timeseries.png?raw=true" title="Time Series">
</p>

- Section 3: Most Common Hashtags
    + 10 most common hashtags as determined by their frequency of occurence weighted by hate score

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/hashtags.png?raw=true" title="Hashtags">
</p>

- Section 4: Top 10 Users Promoting Hate speech
    + Rated by the average hate score of their tweets
    + Also included: their most recent followers count to indicate their infulence within the network

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/top10users.png?raw=true" title="Top10Users">
</p>

- Section 5: Hate Speech geographical Hot Spots
    + Average hate score by country (Global) or state (US only)
    + The global map is sparsely populated mostly due to English language restriction, not because hate speech is not common there

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/usa.png?raw=true" title="USA">
</p>

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/global.png?raw=true" title="Global">
</p>


&nbsp;

### Replication

All the scripts necessary to replicate our work are provided in this repo:

- [streaming](https://github.com/YuliaZamriy/W251-final-project/tree/master/streaming) folder contains all the scripts for collecting streaming data from Twitter, including how to set up `kafka` and run `scala` scripts. 
- [classify](https://github.com/YuliaZamriy/W251-final-project/tree/master/classify) folder contains all the scripts for running the model including the data used in the original research
- [analyze](https://github.com/YuliaZamriy/W251-final-project/tree/master/analyze) folder contains all the scripts necessary for populating and running the dashboard
    + [data](https://github.com/YuliaZamriy/W251-final-project/tree/master/analyze/data) sub-folder contains a small portion of data collected from Twitter before classification

&nbsp;

### Future Work

This project is only the first step in analyzing hate speech in real time. There are many directions that we can take, but next steps can be broken down into two categories:

1. *Framework: Improving hate speech classifier*
    - As of this moment we have implemented only one of the existing models. There are quite a few others we could test and possibly build an ensemble solution. Another alternative would be to leverage [Perspective API](https://github.com/conversationai/perspectiveapi) that identifies `toxic` speech.
    - One of the keys to building a robust classifier is quality labels. Hence, extending training dataset could help us improve the model. One of the most common crowd sourcing platforms is [Amazon Mechanical Turk](https://www.mturk.com/,) and we could use it to label new data. 
    - Add granularity to classification of hate speech (misogynist, homophobic, racist, etc.).
2. *Dashboard: Adding more context for the analysis*
    - Combine hate speech locations with reports of crime
    - Add the option to extend the timeline beyond 24 hours
    - Introduce more languages
    - Ability to export the underlying data (currently it's possible only by clicking on `Edit in Chart Studio` button associated with each chart)
    - Add a live feed of hate speech along with relevant news feeds
    - Many others
