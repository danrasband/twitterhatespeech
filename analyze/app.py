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
# loading the data

hate_tweets_df = helpers.hate_tweets_df

# Chart #1: Time series
by_hour_df = helpers.by_hour_df

trace1_ch1 = go.Scatter(
    x=by_hour_df['day-hour'],
    y=by_hour_df['hate_score'],
    line={'color': '#144F6F'}
)

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
    x=random.choices(range(2 * n_hashtags), k=n_hashtags),
    y=random.choices(range(3 * n_hashtags), k=n_hashtags),
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
              'range': [-2, 2 * n_hashtags + 2]},
    'yaxis': {'showgrid': False,
              'showticklabels': False,
              'zeroline': False,
              'range': [-1, 3 * n_hashtags + 1]},
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
        'color': '#144F6F'
    },
    name='Followers Count',
    orientation='h',
)

trace2_ch3 = go.Scatter(
    x=top_haters_df['probability_hate'],
    y=top_haters_df['screen_name'],
    mode='lines+markers',
    line={'color': '#144F6F'},
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

scl = [[0.0, '#BDD4DD'],
       [0.1, '#A7C3CF'],
       [0.2, '#88A7B4'],
       [0.3, '#7498A7'],
       [0.4, '#628695'],
       [0.5, '#517685'],
       [0.6, '#3F6676'],
       [0.7, '#2F5767'],
       [0.8, '#244B5B'],
       [0.9, '#1A4252'],
       [1.0, '#123847']]

today_string = dt.today().strftime('%B %d, %Y %H:%M')
ttl_count = helpers.hate_tweets_df.shape[0]

# Application

app.layout = html.Div(children=[
    html.Div(
        children=[
            html.H1(
                children='Hate Speech on Twitter'
            ),
            html.H2(
                children='Real Time Analysis of Hate Activity on the Leading Social Platform'
            )],
        style={
            'textAlign': 'center',
            'backgroundColor': '#212F3D',
            'color': '#F8F9F9'
        }),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.H3(
                        children='Updated: ' + today_string
                    ),
                    html.H3(
                        children='Total number of tweets with high likelihood of hate speech collected: ' + str(ttl_count)
                    ),
                    dcc.Markdown('#### Project information is on [GitHub](https://github.com/YuliaZamriy/W251-final-project)')
                ]
            )
        ],
        style={
            'textAlign': 'left',
            'color': '#212F3D'
        }
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
            dcc.Dropdown(
                id='map-scope',
                options=[
                    {'label': 'United States', 'value': 'USA'},
                    {'label': 'Global', 'value': 'World'}
                ],
                value='USA'
            ),
            dcc.Graph(id='hate-map')
        ], style={'width': '49%',
                  'padding': 10,
                  'display': 'inline-block'})
])


@app.callback(
    dash.dependencies.Output('hate-map', 'figure'),
    [dash.dependencies.Input('map-scope', 'value')])
def update_map(value):

    full_map_df = helpers.full_map_df
    full_map_df = full_map_df[full_map_df['level'] == value]

    if value == 'USA':

        trace1_ch4 = {
            'type': 'choropleth',
            'colorscale': scl,
            'autocolorscale': False,
            'locations': full_map_df['code'],
            'z': full_map_df['avg_score'],
            'locationmode': 'USA-states',
            'text': full_map_df['name'],
            'marker': {
                    'line': {
                        'color': 'rgb(255,255,255)',
                        'width': 2
                    }},
            'colorbar': {'title': "Hate Meter",
                         'titlefont': {'size': 16}}
        }

        layout1_ch4 = {
            'title': 'Hate Speech Geographical Hot Spots',
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

    else:

        trace1_ch4 = {
            'type': 'choropleth',
            'colorscale': scl,
            'autocolorscale': False,
            'locations': full_map_df['code'],
            'z': full_map_df['avg_score'],
            'text': full_map_df['name'],
            'marker': {
                    'line': {
                        'color': 'rgb(255,255,255)',
                        'width': 0.5
                    }},
            'colorbar': {'title': "Hate Meter",
                         'titlefont': {'size': 16}}
        }

        layout1_ch4 = {
            'title': 'Hate Speech Geographical Hot Spots',
            'titlefont': {'size': 36},
            'geo': {
                'projection': {'type': 'Mercator'},
                'showframe': False,
                'showlakes': True,
                'showcoastlines': False,
                'lakecolor': 'rgb(255, 255, 255)'
            }
        }

    return {
        'data': [trace1_ch4],
        'layout': layout1_ch4
    }


if __name__ == '__main__':
    app.run_server(debug=True)
