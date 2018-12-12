#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import random
import helpers
from plotly import tools


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# https://htmlcolorcodes.com/
colors = {
    'background': '#212F3D',
    'text': '#F8F9F9'
}


# loading the data

tweet_df, tweet_dict = helpers.LoadData('Data/tweets.json')
retweet_df, retweet_dict = helpers.LoadData('Data/retweets.json')

# Chart #1: Time series
by_hour = pd.DataFrame(tweet_df['hate_count'].groupby([tweet_df['created'].dt.date.rename('day'), tweet_df['created'].dt.hour.rename('hour')]).sum())
by_hour.reset_index(inplace=True)
by_hour['day-hour'] = by_hour['day'].map(str) + " : " + by_hour['hour'].map(str)


# Chart #2: Most common hashtags
# source: https://community.plot.ly/t/wordcloud-in-dash/11407/4
re_hash = {}
for tweet in retweet_dict:
    words = retweet_dict[tweet]['text'].split(" ")
    for word in words:
        if word and word[0] == "#":
            if word not in re_hash:
                re_hash[word] = [retweet_dict[tweet]['retweet_count']]
            else:
                re_hash[word][0] += retweet_dict[tweet]['retweet_count']

re_hash_df = pd.DataFrame.from_dict(re_hash, orient='index')
re_hash_df.rename(columns={0: 'count'}, inplace=True)

n_hashtags = 20
pop_hashtags = re_hash_df.sort_values(by=["count"], ascending=False).index[:n_hashtags]

counts = np.array(re_hash_df.sort_values(by=["count"], ascending=False)['count'][:n_hashtags])
weights = 10 * counts / counts[np.argmin(counts)]
color_count = int(n_hashtags / 10)
colors_wc = color_count * ['#17202A', '#1B2631', '#273746', '#4D5656', '#424949', '#566573', '#707B7C', '#808B96', '#839192', '#95A5A6']

# Chart #3: Haters

n_haters = 10

users_hs = {}
for tweet in retweet_dict:
    if retweet_dict[tweet]['username'] not in users_hs:
        users_hs[retweet_dict[tweet]['username']] = 1
    else:
        users_hs[retweet_dict[tweet]['username']] += 1

top_haters = sorted(users_hs.items(), key=lambda x: -x[1])[:n_haters]

hater_dict = {}
for hater in top_haters:
    try:
        hater_dict[hater[0]] = helpers.getUserData(hater[0])
        hater_dict[hater[0]]['hate_score'] = hater[1]
    except:
        hater_dict[hater[0]] = {"name": "SUSPENDED", 'hate_score': hater[1]}

hater_df = pd.DataFrame.from_dict(hater_dict, orient="index")
suspended = hater_df['screen_name'].loc[hater_df["name"] == "SUSPENDED"]
hater_df = hater_df.loc[hater_df['name'] != "SUSPENDED"]

# source: https://plot.ly/python/horizontal-bar-charts/
trace0 = go.Bar(
    x=hater_df['followers_count'],
    y=hater_df['screen_name'],
    marker={
        'color': 'rgba(50, 171, 96, 0.6)',
        'line': {'color': 'rgba(50, 171, 96, 1.0)',
                 'width': 1},
    },
    name='Followers Count',
    orientation='h',
)

trace1 = go.Scatter(
    x=hater_df['hate_score'],
    y=hater_df['screen_name'],
    mode='lines+markers',
    line={'color': 'rgb(128, 0, 128)'},
    name='Hate Score',
)

layout = dict(
    title='Top 10 Users Promoting Hate Speech',
    yaxis=dict(
        showgrid=False,
        showline=False,
        showticklabels=True,
        domain=[0, 0.85],
    ),
    yaxis2=dict(
        showgrid=False,
        showline=True,
        showticklabels=False,
        linecolor='rgba(102, 102, 102, 0.8)',
        linewidth=2,
        domain=[0, 0.85],
    ),
    xaxis=dict(
        zeroline=False,
        showline=False,
        showticklabels=True,
        showgrid=True,
        domain=[0, 0.42],
    ),
    xaxis2=dict(
        zeroline=False,
        showline=False,
        showticklabels=True,
        showgrid=True,
        domain=[0.47, 1],
        side='top',
    ),
    legend=dict(
        x=0.029,
        y=1.038,
        font=dict(
            size=10,
        ),
    ),
    margin=dict(
        l=100,
        r=20,
        t=70,
        b=70,
    ),
    # paper_bgcolor='rgb(248, 248, 255)',
    # plot_bgcolor='rgb(248, 248, 255)',
)


fig = tools.make_subplots(
    rows=1,
    cols=2,
    specs=[[{}, {}]],
    shared_xaxes=True,
    shared_yaxes=False,
    vertical_spacing=0.001)

fig.append_trace(trace0, 1, 1)
fig.append_trace(trace1, 1, 2)
fig['layout'].update(layout)

# Chart #4: Map
# source: https://plot.ly/python/choropleth-maps/

places_dict = {}
for tweet in retweet_dict:
    if retweet_dict[tweet]['place'] not in places_dict:
        places_dict[retweet_dict[tweet]['place']] = 1
    else:
        places_dict[retweet_dict[tweet]['place']] += 1

states = helpers.states
states_dict = {state: [0] for state in states}
for place in places_dict:
    place_list = place.split()
    if len(place_list) == 2:
        if place_list[1] in states_dict:
            states_dict[place_list[1]][0] += 1
        elif place_list[1] == 'USA':
            if place_list[0] in states.values():
                for abbr, full in states.items():
                    if full == place_list[0]:
                        states_dict[abbr][0] += 1

hate_map = pd.DataFrame.from_dict(states_dict, orient="index")
hate_map.reset_index(inplace=True)
hate_map.rename(columns={'index': 'state', 0: 'hate_count'}, inplace=True)


scl = [[0.0, 'rgb(242,240,247)'], [0.2, 'rgb(218,218,235)'], [0.4, 'rgb(188,189,220)'],
       [0.6, 'rgb(158,154,200)'], [0.8, 'rgb(117,107,177)'], [1.0, 'rgb(84,39,143)']]

chart3_data = [dict(
    type='choropleth',
    colorscale=scl,
    autocolorscale=False,
    locations=hate_map['state'],
    z=hate_map['hate_count'],
    locationmode='USA-states',
    # text=df['text'],
    marker=dict(
        line=dict(
            color='rgb(255,255,255)',
            width=2
        )),
    colorbar=dict(
        title="Hate Meter")
)]

chart3_layout = dict(
    title='USA Hate Speech',
    geo=dict(
        scope='usa',
        projection=dict(type='albers usa'),
        showlakes=True,
        lakecolor='rgb(255, 255, 255)'),
)

chart3_fig = dict(data=chart3_data, layout=chart3_layout)

# Application

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Hate Speech on Twitter',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H2(
        children='Real Time Analysis of Hate Activity on the Leading Social Platform',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(
        [
            dcc.Graph(
                id='tweets-by-hour1',
                figure={
                    'data': [
                        go.Scatter(
                            x=by_hour['day-hour'],
                            y=by_hour['hate_count'],
                        )
                    ],
                    'layout': go.Layout(
                        title='Hourly Activity',
                        xaxis={'showgrid': False, 'title': 'Day : Hour'},
                        yaxis={'showgrid': False, 'title': 'Number of Tweets with Hate Speech'},
                        # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1}
                    )
                }
            ),
            dcc.Graph(
                id='hashtags',
                figure={
                    'data': [
                        go.Scatter(
                            x=random.choices(range(n_hashtags), k=n_hashtags),
                            y=random.choices(range(n_hashtags), k=n_hashtags),
                            mode='text',
                            text=pop_hashtags,
                            marker={'opacity': 0.3},
                            textfont={'size': weights,
                                      'color': colors_wc}
                        )
                    ],
                    'layout': go.Layout(
                        title='Most Common Hashtags',
                        xaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False, 'range': [-1, n_hashtags + 1]},
                        yaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False, 'range': [-1, n_hashtags + 1]},
                        # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    )
                }
            )], style={'width': '49%', 'display': 'inline-block'}),
    html.Div(
        [
            dcc.Graph(
                id='haters',
                figure=fig
            ),
            dcc.Graph(
                id='hate-map',
                figure=chart3_fig
            )], style={'width': '49%', 'display': 'inline-block'})
])

if __name__ == '__main__':
    app.run_server(debug=True)
