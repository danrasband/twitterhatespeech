#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import random
from datetime import datetime as dt
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

hate_tweets_df = helpers.hate_tweets_df

# Chart #1: Time series
by_hour_df = helpers.by_hour_df

trace1_ch1 = go.Scatter(
    x=by_hour_df['day-hour'],
    y=by_hour_df['hate_score'],)

layout_ch1 = {
    'title': 'Hourly Activity',
    'titlefont': {'size': 36},
    'xaxis': {'showgrid': False},
    'yaxis': {'showgrid': True,
              'title': 'Total Hate Score',
              'titlefont': {'size': 16}},
    'legend': {'x': 0, 'y': 1}
}

fig_ch1 = {'data': [trace1_ch1],
           'layout': layout_ch1}

# Chart #2: Most common hashtags
# source: https://community.plot.ly/t/wordcloud-in-dash/11407/4

# input the number of top hashtags to output
top_hash_df = helpers.top_hash_df

n_hashtags = 10
top_hash = top_hash_df.sort_values(by=["count"], ascending=False).index[:n_hashtags]

# font size for the top hashtags
weights = [random.randint(15, 35) for i in range(n_hashtags)]

# color paletter for the top hashtags
color_count = int(n_hashtags / 10)
colors_wc = color_count * ['#17202A',
                           '#1B2631',
                           '#273746',
                           '#4D5656',
                           '#424949',
                           '#566573',
                           '#707B7C',
                           '#808B96',
                           '#839192',
                           '#95A5A6']

trace1_ch2 = go.Scatter(
    x=random.choices(range(n_hashtags), k=n_hashtags),
    y=random.choices(range(n_hashtags), k=n_hashtags),
    mode='text',
    text=top_hash,
    marker={'opacity': 0.3},
    textfont={'size': weights,
              'color': colors_wc}
)

layout_ch2 = {
    'title': 'Most Common Hashtags',
    'titlefont': {'size': 36},
    'xaxis': {'showgrid': False,
              'showticklabels': False,
              'zeroline': False,
              'range': [-2, n_hashtags + 2]},
    'yaxis': {'showgrid': False,
              'showticklabels': False,
              'zeroline': False,
              'range': [-1, n_hashtags + 1]},
    # 'paper_bgcolor':'#7f7f7f',
    # plot_bgcolor: '#444',
}

fig_ch2 = {'data': [trace1_ch2],
           'layout': layout_ch2}

# Chart #3: Haters

top_haters_df = helpers.top_haters_df


# source: https://plot.ly/python/horizontal-bar-charts/
trace1_ch3 = go.Bar(
    x=top_haters_df['followers_count'],
    y=top_haters_df['screen_name'],
    marker={
        'color': 'rgb(117,107,177)'
    },
    name='Followers Count',
    orientation='h',
)

trace2_ch3 = go.Scatter(
    x=top_haters_df['hate_score'],
    y=top_haters_df['screen_name'],
    mode='lines+markers',
    line={'color': 'rgb(117,107,177)'},
    name='Hate Score',
)

layout_ch3 = {
    'title': 'Top 10 Users Promoting Hate Speech',
    'titlefont': {'size': 36},
    'yaxis': {
        'showgrid': False,
        'showline': False,
        'showticklabels': True,
        'domain': [0, 0.85],
    },
    'yaxis2': {
        'showgrid': False,
        'showline': True,
        'showticklabels': False,
        'linecolor': 'rgba(102, 102, 102, 0.8)',
        'linewidth': 2,
        'domain': [0, 0.85],
    },
    'xaxis': {
        'zeroline': False,
        'showline': False,
        'showticklabels': True,
        'showgrid': True,
        'domain': [0, 0.42],
    },
    'xaxis2': {
        'zeroline': False,
        'showline': False,
        'showticklabels': True,
        'showgrid': True,
        'domain': [0.47, 1],
        'side': 'top',
    },
    'legend': {
        'x': 0.029,
        'y': 1.038,
        'font': {'size': 16}
    },
    'margin': {
        'l': 100, 'r': 20, 't': 70, 'b': 70,
    }}


fig_ch3 = tools.make_subplots(
    rows=1,
    cols=2,
    specs=[[{}, {}]],
    shared_xaxes=True,
    shared_yaxes=False,
    vertical_spacing=0.001)

fig_ch3.append_trace(trace1_ch3, 1, 1)
fig_ch3.append_trace(trace2_ch3, 1, 2)
fig_ch3['layout'].update(layout_ch3)

# Chart #4: Map
# source: https://plot.ly/python/choropleth-maps/

full_map_df = helpers.full_map_df

states_df = full_map_df[full_map_df['level'] == 'USA']
world_df = full_map_df[full_map_df['level'] == 'World']

scl = [[0.0, 'rgb(242,240,247)'],
       [0.2, 'rgb(218,218,235)'],
       [0.4, 'rgb(188,189,220)'],
       [0.6, 'rgb(158,154,200)'],
       [0.8, 'rgb(117,107,177)'],
       [1.0, 'rgb(84,39,143)']]


trace1_ch4 = {
    'type': 'choropleth',
    'colorscale': scl,
    'autocolorscale': False,
    'locations': states_df['code'],
    'z': states_df['avg_score'],
    'locationmode': 'USA-states',
    # text=df['text'],
    'marker': {
            'line': {
                'color': 'rgb(255,255,255)',
                'width': 2
            }},
    'colorbar': {'title': "Hate Meter",
                 'titlefont': {'size': 16}}
}

trace2_ch4 = {
    'type': 'choropleth',
    'colorscale': scl,
    'autocolorscale': False,
    'locations': world_df['code'],
    'z': world_df['avg_score'],
    # text=df['text'],
    'marker': {
            'line': {
                'color': 'rgb(255,255,255)',
                'width': 0.5
            }},
    'colorbar': {'title': "Hate Meter",
                 'titlefont': {'size': 16}}
}

layout1_ch4 = {
    'title': 'Hate Speech Hot Spots',
    'titlefont': {'size': 36},
    'geo': {
        'scope': 'usa',
        'projection': {'type': 'albers usa'},
        'showframe': False,
        'showlakes': True,
        'showcoastlines': False,
        'lakecolor': 'rgb(255, 255, 255)'
    }
}

layout2_ch4 = {
    'title': 'Hate Speech Hot Spots',
    'titlefont': {'size': 36},
    'geo': {
        'projection': {'type': 'Mercator'},
        'showframe': False,
        'showlakes': True,
        'showcoastlines': False,
        'lakecolor': 'rgb(255, 255, 255)'
    }
}

fig_ch4 = {'data': [trace2_ch4],
           'layout': layout2_ch4}

today_string = dt.today().strftime('%B %d, %Y')
ttl_count = helpers.hate_tweets_df.shape[0]

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
        className='row',
        children=[
            html.Div(
                className='ten columns',
                children=[
                    html.H3(
                        children='Updated: ' + today_string,
                        style={
                            'textAlign': 'left',
                            'color': colors['text']
                        }
                    ),
                    html.H3(
                        children='Total number of tweets with high likelihood of hate speech collected: ' + str(ttl_count),
                        style={
                            'textAlign': 'left',
                            'color': colors['text']
                        }
                    ),

                ]
            )
        ]
    ),
    html.Div(
        [
            dcc.Graph(
                id='tweets-by-hour',
                figure=fig_ch1
            ),
            dcc.Graph(
                id='hashtags2',
                figure=fig_ch2
            )], style={'width': '49%',
                       'padding': 10,
                       'display': 'inline-block'}),

    html.Div(
        [
            dcc.Graph(
                id='haters',
                figure=fig_ch3
            ),
            dcc.Graph(
                id='hate-map',
                figure=fig_ch4
            )], style={'width': '49%',
                       'padding': 10,
                       'display': 'inline-block'})
])

if __name__ == '__main__':
    app.run_server(debug=True)
