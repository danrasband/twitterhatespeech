# Real Time Monitoring of Hate Speech on Twitter

## Final Project for "W251. Scaling Up! Real Big Data" 
#### Master of Information and Data Science at UC Berkeley School of Information

&nbsp;

### Dan Rasband and Yulia Zamriy 
#### December 17th, 2018

&nbsp;

### Introduction

Social platforms have become our everyday reality. We use them for connecting with friends, checking news, sharing content. They cross boudnaries and open doors, they level the playing field. But as much as they are praised for being a platform for equality and empowerment, they also bear responsibility for uncovering and fueling hate in cyber space, which frequently leads to violence in the physical world. 

One of the main issues that prohibits social networks from creating guidelines on communication descency is the lack of legislation that defines hate speech. But beyond legislation, how do we define hate speech? How do we create an objective definition beyond personal opinions? And how do we not violate the First Amendment? 

Many attempts have been made to use machine learning in classifying hate speech: [Waseem](http://aclweb.org/anthology/N16-2013), [Gröndahl](https://arxiv.org/abs/1808.09115), [Davidson](https://arxiv.org/abs/1703.04009), [Malmasi](https://arxiv.org/abs/1712.06427), [Zhang](https://arxiv.org/abs/1803.03662) and many others. But most of them still live in research papers of their original authors. Companies like Twitter also work proactively to identify and remove tweets and accounts that vioalte their ever changing policies. And yet, we still have no clear visibility of how deep the issue is and how well social media companies are at dealing with it. 

Our main goal for this project is to provide public with open and simple visualizations about the proliferation of hate speech on Twitter using (behind the scences but open to everyone to explore) machine learning algorithms. Our dashboard answers questions such as:

- How bad is hate speech situation now on Twitter? Is it getting better or worse over time?
- What are the hashtags used by people promoting hate speech?
- Who are the worst offenders and how visible they are in the network?
- What are the hotspots of hate speech across the globe?


### Background

The First Amendment to the US Constitution, ratified on December 15, 1791, states that:
> **Congress shall make no law** respecting an establishment of religion, or prohibiting the free exercise thereof; or **abridging the freedom of speech, or of the press**; or the right of the people peaceably to assemble, and to petition the Government for a redress of grievances.

The amendment was designed to protect our ability to express our opinions through speech, actions, written text, appearance and other forms of expression. It's at the core of the US democracy.

We are all well aware of the ongoing debate about the definition and scope of free speech. There are a lot of opinions, and frequently the loudests but not necessarily the most objective stand out. However, as data scientists we firmly believe that on the aggregate level, when the opinions are measured and averaged across cultures, societies, and continents, the definition can become more objective and actually implementable. That's the power of machine learning algorithms applied to labeled data. 

After researching the above mentioned research papers on hate speech identification, we selected ["Automated Hate Speech Detection and the Problem of Offensive Language"](https://github.com/t-davidson/hate-speech-and-offensive-language) by [Davidson](https://arxiv.org/abs/1703.04009) for our baseline model because:

- It contains the underlying data with tweets classified as `hate speech`, `offensive language` and `other` that we can use to retrain the model
- We successfully replicated the model based on their data and code
- The authors achieved reasonable accuracy
- The output contains probabilities that we can use to assess the severity of the problem
- This research is relatively recent

An additional source of inspiration was the [Extreme Right Dashoboard](https://extremeright.thinkprogress.org/) by [ThinkProgress](https://thinkprogress.org/). However, their analysis is focused on scraping the data on a short list of users that have certain key words in their profiles or names (for example, `alt-right`, `red-pill`, `fashy`, `14/88`, `identitarian`, `nationalist`). The issue with this approach is that hate speech is not limited to self proclaimed nationalists. Moreover, users desribing themselves as far right do not necessarily use hate speech, at least not often. The counter argument to that critisism could be that a lot of hate speech can be implied in othewise innocent words. Our goal is to use an algorithm that can objectively detect elements of hate speech, and no well researched algorithm so far has been able to decipher implied meanings (at least to our best knowledge). 

### The Data

For model training we used labeled [data](https://github.com/t-davidson/hate-speech-and-offensive-language/tree/master/data) from Davidson that contains around 24k tweets that were classified as hate speech (0), offensive language (1) and neight (2). The labels were obtained through CrowdFlower (now [Figure Eight](https://www.figure-eight.com/)); the original researchers keept the tweets that were coded by at least 3 people.

<p align="center">
  <img src="https://github.com/YuliaZamriy/W251-final-project/blob/master/images/hist_012.png?raw=true" width="350" height="250" title="Histogram of Target">
</p>

We launched data collection on **TODO include date** and as of December 15th, 2018 classified 21,748 as hate speech based on **TODO include cutoff** probability as a cutoff.

### Model

**TODO: very briefly describe the model and list most important features and model performance**


### Infrasturcture

### Dashboard

### Future Work
