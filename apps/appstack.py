import os
import pickle
import copy
import psycopg2
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
import plotly.tools as tls
from io import StringIO
import numpy as np

import  plotly.plotly as py
import plotly.graph_objs as go

from rq import Queue
from worker import conn
from utils import count_words_at_url

from app import app

mapbox_access_token = "pk.eyJ1IjoiamFja3AiLCJhIjoidGpzN0lXVSJ9.7YK6eRwUNFwd3ODZff6JvA"
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501


q = Queue(connection=conn)
result = q.enqueue(count_words_at_url, 'http://heroku.com')

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'  # noqa: E501
    })

# Postgres to python connect through psycopg2
os.environ['DATABASE_URL'] = "postgres://u4sgkhh7ulkcqi:p8d619707d6fd988ed13425a1d337aed73e90c0678f2646caff7f7ee9666d8410@ec2-34-230-211-89.compute-1.amazonaws.com:5432/d7optpplabpolr"
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


# Global chart template

# App layout
layout = html.Div(
    [
        dcc.Tabs(id="shelldbtabs", value='global', children=[
            dcc.Tab(label='Global', value='global'),
            dcc.Tab(label='MESA', value='mesa'),
            dcc.Tab(label='Russia', value='russia'),
            dcc.Tab(label='APAC', value='apac'),
            dcc.Tab(label='China', value='china'),
            dcc.Tab(label='EU', value='eu')
        ])
        html.Div(id='shelldbcontent')
    ]
)

@app.callback(Output('shelldbcontent', 'children'),
              [Input('shelldbtabs', 'value')])

def render_content(tab):
    if tab == 'global':
        return


        html.Div(     #Title and Gfk Image
            [
                html.H1(
                    'GfK POS DASHBOARD',
                    className='eleven columns',
                ),
                html.Img(
                    src="https://www.gfk.com/fileadmin/fe/gfktheme/images/favicons/apple-touch-icon-72x72.png",
                    className='one columns',
                    style={
                        'height': '70',
                        'width': '70',
                        'float': 'right',
                        'position': 'relative',
                    },
                ),
            ],
            className='row'
        ),
        html.Br(),
        html.Div([
            html.Div([
                html.P('Select Global Region:')
            ],className='two columns'),
            dcc.RadioItems(
                id='globalregion',
                options=[
                    {'label': 'GLOBAL  ', 'value': 'allreg'},
                    {'label': 'MESA  ', 'value': 'mena'},
                    {'label': 'APAC  ', 'value': 'apac'},
                    {'label': 'RUSSIA  ', 'value': 'rus'},
                    {'label': 'CHINA  ', 'value': 'china'},
                    {'label': 'EU  ', 'value': 'eu'}
                ],
                labelStyle={'display': 'inline-block'}
            ),
            html.Div([
                html.P('Note: Only MENA & Russia operational for brandshares and distribution performance charts. All countries and region data available for all other charts.')
            ],className='nine columns', style= {'display': 'inline-block','color': 'red'}),
        ],className='row'),

        html.Div([
            html.Div([
                html.P('Select Analysis Type:')
            ],className='two columns'),
            dcc.RadioItems(
                id='analysistype',
                options=[
                    {'label': 'By Channel  ', 'value': 'channel_analysis'},
                    {'label': 'By Region  ', 'value': 'region_analysis'}
                ],
                labelStyle={'display': 'inline-block'}
            ),
            html.Div([
                html.P('Note: Selecting an option will disable the other. For example, selecting By Region will disable Select Channel dropdown')
            ],className='nine columns', style= {'display': 'inline-block','color': 'red'}),
        ],className='row'),

        html.Br(),
        html.Div([
            html.Div([
                html.P('Select Country:'),
                dcc.Dropdown(
                    id='country',
                    placeholder="Country",
                ),
            ],className='two columns'),

            html.Div([
                html.P('Select Engine Oil Type:'),
                dcc.Dropdown(
                    id='typeveh',
                    placeholder="Type Of Vehicle",
                ),
            ],className='two columns'),

            html.Div([
                html.P('Select Region:'),
                dcc.Dropdown(
                    id='region',
                    placeholder="Region",
                ),
            ],className='two columns'),

            html.Div([
                html.P('Select Channel:'),
                dcc.Dropdown(
                    id='channel',
                    placeholder="Channel",
                ),
            ],className='two columns'),

            html.Div([
                html.P('Select Oil Base:'),
                dcc.Dropdown(
                    id='base',
                    placeholder="Base",
                ),
            ],className='two columns')
        ],className='row'),

        #QoQ Brandshares Div
        html.Div([
            html.Div([
                dcc.Graph(
                    id='brandshares',
                    config={'displayModeBar': False},
                )
            ],className='six columns'),

            html.Div([
                dcc.Graph(
                    id='brandshares2',
                    config={'displayModeBar': False},
                )
            ],className='six columns')
        ],className='row'),

        #YoY Brandshares Div
        html.Div([
            html.Div([
                dcc.Graph(
                    id='brandshares3',
                    config={'displayModeBar': False},
                )
            ],className='six columns'),

            html.Div([
                dcc.Graph(
                    id='brandshares4',
                    config={'displayModeBar': False},
                )
            ],className='six columns')
        ],className='row'),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='distbrand',
                    config={'displayModeBar': False}
                ),
            ],className='row'),

        ]),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='pie',
                    config={'displayModeBar': False}
                ),
            ],className='row'),

        ]),

        html.Div([
            html.Div([
                dcc.Graph(
                    id='horizbar',
                    config={'displayModeBar': False}
                ),
            ],className='row'),

        ]),

        html.Br(),
        html.Br(),
        html.Div([
            html.Div([
                dcc.Graph(
                    style={'height': '700px'},
                    id='skubar',
                    config={'displayModeBar': False}
                ),
            ]),
        ],className='row'),
        html.Br(),
        html.Br(),
    ],
    style={'font-family': 'Calibri Light'},className='ten columns offset-by-one'
)

########<Options for dropdowns Callbacks>########

@app.callback(
    Output('country','options'),
    [Input('globalregion','value')]
)

def update_typeveh(selected_globalregion):

    if(selected_globalregion=='allreg'):
        return [
            {'label': 'China', 'value': 'China'},
            {'label': 'Indonesia', 'value': 'Indonesia'},
            {'label': 'Thailand', 'value': 'Thailand'},
            {'label': 'Malaysia', 'value': 'Malaysia'},
            {'label': 'Oman', 'value': 'Oman'},
            {'label': 'Saudi Arabia', 'value': 'Saudi Arabia'},
            {'label': 'United Arab Emirates', 'value': 'United Arab Emirates'},
            {'label': 'Egypt', 'value': 'Egypt'},
            {'label': 'Russia', 'value': 'Russia'}
        ]
    elif(selected_globalregion=='mena'):
        return [
            {'label': 'MESA', 'value': ' '},
            {'label': 'Oman', 'value': 'Oman'},
            {'label': 'Saudi Arabia', 'value': 'Saudi Arabia'},
            {'label': 'United Arab Emirates', 'value': 'United Arab Emirates'},
            {'label': 'Egypt', 'value': 'Egypt'},
        ]
    elif(selected_globalregion=='apac'):
        return [
            {'label': 'APAC', 'value': 'APAC'},
            {'label': 'Indonesia', 'value': 'Indonesia'},
            {'label': 'Thailand', 'value': 'Thailand'},
            {'label': 'Malaysia', 'value': 'Malaysia'},
        ]
    elif(selected_globalregion=='china'):
        return [
            {'label': 'China', 'value': 'China'},
        ]
    if(selected_globalregion=='rus'):
        return [
            {'label': 'Russia', 'value': 'Russia'},
        ]
#Vehicle type button options
@app.callback(
    Output('typeveh','options'),
    [Input('analysistype','value'),
     Input('country','value')]
)

def update_typeveh(analysistype_val,selected_country):

    if analysistype_val=='region_analysis':
        SQL="SELECT DISTINCT(typeveh) FROM brandshares_region WHERE ctry=(%s)"
    elif analysistype_val=='channel_analysis':
        SQL="SELECT DISTINCT(typeveh) FROM brandshares_channel WHERE ctry=(%s)"

    cur.execute(SQL,(selected_country,))
    result=cur.fetchall()
    typeveh_options = zip(*result)
    print(typeveh_options)
    opt=np.array(list(typeveh_options))
    print(opt)
    return [{'label': i, 'value': i} for i in opt[0]]

@app.callback(Output('typeveh', 'value'),
              [Input('typeveh', 'options')]
)

def set_typeveh_value(available_options):
    return available_options[2]['value']

#region button options
@app.callback(
    Output('region','options'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value')]
)

def update_typeveh(analysistype_val,
                   selected_country,
                   selected_typeveh):

    if analysistype_val=='channel_analysis':
        return [{'label': 'Disabled', 'value': 'Disabled'}]
    elif analysistype_val=='region_analysis':
        SQL="SELECT DISTINCT(region) FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s)"
        cur.execute(SQL,(selected_country,selected_typeveh,))
        result=cur.fetchall()
        region_options = zip(*result)
        print(region_options)
        opt=np.array(list(region_options))
        print(opt)
        return [{'label': i, 'value': i} for i in opt[0]]

@app.callback(Output('region', 'value'),
              [Input('analysistype','value'),
               Input('region', 'options')]
)

def set_region_value(analysistype_val,available_options):

    if analysistype_val=='channel_analysis':
        return available_options[0]['value']

    elif analysistype_val=='region_analysis':
        return available_options[3]['value']


#Channel button options
@app.callback(
    Output('channel','options'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value')]
)

def update_typeveh(analysistype_val,
                   selected_country,
                   selected_typeveh):

    if analysistype_val=='region_analysis':
        return [{'label': 'Disabled', 'value': 'Disabled'}]
    elif analysistype_val=='channel_analysis':
        SQL="SELECT DISTINCT(channel) FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s)"
        cur.execute(SQL,(selected_country,selected_typeveh,))
        result=cur.fetchall()
        channel_options = zip(*result)
        print(channel_options)
        opt=np.array(list(channel_options))
        print(opt)
        return [{'label': i, 'value': i} for i in opt[0]]

@app.callback(Output('channel', 'value'),
              [Input('analysistype','value'),
               Input('channel', 'options')]
)

def set_region_value(analysistype_val,available_options):

    if analysistype_val=='region_analysis':
        return available_options[0]['value']

    elif analysistype_val=='channel_analysis':
        return available_options[3]['value']

#Base button options
@app.callback(
    Output('base','options'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value')]
)

def update_typeveh(analysistype_val,
                   selected_country,
                   selected_typeveh,
                   selected_region,
                   selected_channel):

    if analysistype_val=='region_analysis':
        SQL="SELECT DISTINCT(base) FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s)"
        cur.execute(SQL,(selected_country,selected_typeveh,selected_region,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT DISTINCT(base) FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s)"
        cur.execute(SQL,(selected_country,selected_typeveh,selected_channel,))

    result=cur.fetchall()
    base_options = zip(*result)
    print(base_options)
    opt=np.array(list(base_options))
    print(opt)
    return [{'label': i, 'value': i} for i in opt[0]]

@app.callback(Output('base', 'value'),
              [Input('base', 'options')]
)

def set_typeveh_value(available_options):
    return available_options[4]['value']

########<CHARTS>########

########<Brand Share Chart Callbacks - Top Brands>########

#QoQ Chart Callback
@app.callback(
    Output('brandshares','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
     ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name, usedfor_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, salesplkpq, salesplkcq FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, salesplkpq, salesplkcq FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, salesplkpq_val, salesplkcq_val = zip(*result)
    trial_y=brand_val
    periods=['Q1 2018','Q2 2018']
    trial_x1=salesplkpq_val
    trial_x2=salesplkcq_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        return go.Bar(
            x=periods,   # cities name on the y-axis
            y=x,        # monthly total on x-axis
            name=name,
            text=x,
            hoverinfo='text',
            textposition = 'auto',  # label for hover
            orientation='v', # (!) for horizontal bars, default is 'v'
            marker= go.Marker(
                # color=color,        # set bar colors
                line= go.Line(
                    color='white',  # set bar border color
                    width=1         # set bar border width
                )
            ),
            width = 0.3
        )

    data = go.Data([
        make_trace([trial_x1[i], trial_x2[i]], trial_y[i])
        for i in range(m)
    ])

    layout = go.Layout(
        barmode='stack',  # (!) bars are stacked on this plot
        bargap=0,       # (!) spacing (norm. w.r.t axis) between bars
        title='Brand Volume Share Q-o-Q',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig


@app.callback(
    Output('brandshares2','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
     ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name, usedfor_name):


    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, valplkpq, valplkcq FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, valplkpq, valplkcq FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, valplkpq_val, valplkcq_val = zip(*result)

    trial_y=brand_val
    periods=['Q1 2018','Q2 2018']

    trial_x3=valplkpq_val
    trial_x4=valplkcq_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        return go.Bar(
            x=periods,   # cities name on the y-axis
            y=x,        # monthly total on x-axis
            name=name,
            text=x,
            hoverinfo='text',
            textposition = 'auto',  # label for hover
            orientation='v', # (!) for horizontal bars, default is 'v'
            marker= go.Marker(
                # color=color,        # set bar colors
                line= go.Line(
                    color='white',  # set bar border color
                    width=1         # set bar border width
                )
            ),
            width = 0.3
        )

    data = go.Data([
        make_trace([trial_x3[i], trial_x4[i]], trial_y[i]) for i in range(m)
    ])

    layout = go.Layout(
        barmode='stack',  # (!) bars are stacked on this plot
        bargap=0.1,       # (!) spacing (norm. w.r.t axis) between bars
        title='Brand Value Share Q-o-Q (USD)',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig

#YoY Chart Callback
@app.callback(
    Output('brandshares3','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
    ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name, usedfor_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, salesplkpy, salesplkcy FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, salesplkpy, salesplkcy FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, salesplkpy_val, salesplkcy_val = zip(*result)

    trial_y=brand_val
    periods=['YTD 2017','YTD 2018']
    trial_x1=salesplkpy_val
    trial_x2=salesplkcy_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        return go.Bar(
            x=periods,   # cities name on the y-axis
            y=x,        # monthly total on x-axis
            name=name,
            text=x,
            hoverinfo='text',
            textposition = 'auto',  # label for hover
            orientation='v', # (!) for horizontal bars, default is 'v'
            marker= go.Marker(
                # color=color,        # set bar colors
                line= go.Line(
                    color='white',  # set bar border color
                    width=1         # set bar border width
                )
            ),
            width = 0.3
        )

    data = go.Data([
        make_trace([trial_x1[i], trial_x2[i]], trial_y[i])
        for i in range(m)
    ])

    layout = go.Layout(
        barmode='stack',  # (!) bars are stacked on this plot
        bargap=0,       # (!) spacing (norm. w.r.t axis) between bars
        title='Brand Volume Share Y-o-Y (Till June 2018)',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig

@app.callback(
    Output('brandshares4','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
    ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name, usedfor_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, valplkpy, valplkcy FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, valplkpy, valplkcy FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, valplkpy_val, valplkcy_val = zip(*result)

    trial_y=brand_val
    periods=['YTD 2017','YTD 2018']

    trial_x3=valplkpy_val
    trial_x4=valplkcy_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        return go.Bar(
            x=periods,   # cities name on the y-axis
            y=x,        # monthly total on x-axis
            name=name,  # label for hover
            text=x,
            hoverinfo='text',
            textposition = 'auto',
            orientation='v', # (!) for horizontal bars, default is 'v'
            marker= go.Marker(
                # color=color,        # set bar colors
                line= go.Line(
                    color='white',  # set bar border color
                    width=1         # set bar border width
                )
            ),
            width = 0.3
        )

    data = go.Data([
        make_trace([trial_x3[i], trial_x4[i]], trial_y[i]) for i in range(m)
    ])

    layout = go.Layout(
        barmode='stack',  # (!) bars are stacked on this plot
        bargap=0.1,       # (!) spacing (norm. w.r.t axis) between bars
        title='Brand Value Share Y-o-Y (Till June 2018)(USD)',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig


########<Numeric and Weighted Distribution Callbacks>########

@app.callback(
    Output('distbrand','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
    ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name, usedfor_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT brands, wdpq, wdcq, uwdpq, uwdcq FROM distbrand_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT brands, wdpq, wdcq, uwdpq, uwdcq FROM distbrand_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brands_val, wdpq_val, wdcq_val, uwdpq_val, uwdcq_val = zip(*result)

    trace1 = go.Bar(x=brands_val,y=wdpq_val,name="Q1",text=wdpq_val,textposition = 'auto',marker=dict(color='rgba(172,191,233,1)'))
    trace2 = go.Bar(x=brands_val,y=wdcq_val,name="Q2",text=wdcq_val,textposition = 'auto',marker=dict(color='rgba(255,139,164,1)'))

    trace3 = go.Bar(x=brands_val,y=uwdpq_val,name="Q1",text=uwdpq_val,textposition = 'auto',marker=dict(color='rgba(172,191,233,1)'),showlegend=False)
    trace4 = go.Bar(x=brands_val,y=uwdcq_val,name="Q2",text=uwdcq_val,textposition = 'auto',marker=dict(color='rgba(255,139,164,1)'),showlegend=False)

    fig = tls.make_subplots(rows=1, cols=2,shared_xaxes=True,subplot_titles=('Weighted Distribution', 'Unweighted Distribution'))
    fig['layout']['margin'] = {'l': 100, 'r': 120, 'b': 150, 't': 70}

    fig['layout'].update(title='Distribution Performance',titlefont=dict(family='Calibri Light'),barmode='group',hovermode='closest')

    fig.append_trace(trace1,1,1)
    fig.append_trace(trace2,1,1)
    fig.append_trace(trace3,1,2)
    fig.append_trace(trace4,1,2)

    for i in fig['layout']['annotations']:
        i['font'] = dict(family='Calibri Light',size=16)

    return fig

########<Pie Charts Callbacks>########
@app.callback(
    Output('pie','figure'),
    [Input('globalregion','value'),
    ]
)

def update_BS_brands(globalregion_name):

    SQL="SELECT ctry, salesplkq2, valplkq2 FROM pieandbar WHERE globalreg=(%s)"
    cur.execute(SQL,(globalregion_name,))
    result=cur.fetchall()
    ctry_val, salesplkq2_val, valplkq2_val = zip(*result)

    fig = {
        'data': [
            {
                'labels': ctry_val,
                'values': salesplkq2_val,
                'name':'Sales Volume',
                'type': 'pie',
                'domain': {'x': [0, 0.5],
                           'y': [0, 1]},
                'text':'Text D',
                'textposition':'bottom center'
            },
            {
                'labels': ctry_val,
                'name':'Sales Value',
                'values': valplkq2_val,
                'type': 'pie',
                'domain': {'x': [0.5, 1],
                           'y': [0, 1]},
            }
        ],
        'layout': {
            'title':'Country Split (Volume% & Value%)',
        }
    }
    return fig

########<Horizontal Bar Charts Callbacks>########
@app.callback(
    Output('horizbar','figure'),
    [Input('globalregion','value'),
    ]
)

def update_flag(globalregion_name):

    SQL="SELECT ctry, salesplkq1, salesplkq2, shellsalesplkq1, shellsalesplkq2, valplkq1, valplkq2, shellvalplkq1, shellvalplkq2 FROM pieandbar WHERE globalreg=(%s)"
    cur.execute(SQL,(globalregion_name,))
    result=cur.fetchall()
    ctry_val, salesplkq1_val, salesplkq2_val, shellsalesplkq1_val, shellsalesplkq2_val, valplkq1_val, valplkq2_val, shellvalplkq1_val, shellvalplkq2_val = zip(*result)

    trace1 = go.Bar(y=ctry_val,x=salesplkq1_val,name="Q1",orientation='h',text=salesplkq1_val,textposition = 'auto',hoverinfo='skip',marker=dict(color='rgba(255,122,66,1)'))
    trace2 = go.Bar(y=ctry_val,x=salesplkq2_val,name="Q2",orientation='h',text=salesplkq2_val,textposition = 'auto',hoverinfo='skip',marker=dict(color='rgba(90,151,2016,1)'))

    trace3 = go.Bar(y=ctry_val,x=shellsalesplkq1_val,name="Sales Volume",orientation='h',text=shellsalesplkq1_val,textposition = 'auto',hoverinfo='skip',showlegend=False,marker=dict(color='rgba(255,122,66,1)'))
    trace4 = go.Bar(y=ctry_val,x=shellsalesplkq2_val,name="Sales Value",orientation='h',text=shellsalesplkq2_val,textposition = 'auto',hoverinfo='skip',showlegend=False,marker=dict(color='rgba(90,151,2016,1)'))

    trace5 = go.Bar(y=ctry_val,x=valplkq1_val,name="Sales Volume",orientation='h',text=valplkq1_val,textposition = 'auto',hoverinfo='skip',showlegend=False,marker=dict(color='rgba(255,122,66,1)'))
    trace6 = go.Bar(y=ctry_val,x=valplkq2_val,name="Sales Value",orientation='h',text=valplkq2_val,textposition = 'auto',hoverinfo='skip',showlegend=False,marker=dict(color='rgba(90,151,2016,1)'))

    trace7 = go.Bar(y=ctry_val,x=shellvalplkq1_val,name="Sales Volume",orientation='h',text=shellvalplkq1_val,textposition = 'auto',hoverinfo='skip',showlegend=False,marker=dict(color='rgba(255,122,66,1)'))
    trace8 = go.Bar(y=ctry_val,x=shellvalplkq2_val,name="Sales Value",orientation='h',text=shellvalplkq2_val,textposition = 'auto',hoverinfo='skip',showlegend=False,marker=dict(color='rgba(90,151,2016,1)'))

    fig = tls.make_subplots(rows=1, cols=4, shared_yaxes=True,vertical_spacing=0.02,horizontal_spacing=0.05,subplot_titles=('Total Market Sales Volume', 'Shell Sales Volume', 'Total Market Sales Value USD', 'Shell Sales Value USD'))
    fig['layout']['margin'] = {'l': 150, 'r': 20, 'b': 40, 't': 100}

    fig['layout'].update(title='Absolute Volume & Value Figures (Millions) - Q1 2018 vs Q2 2018',titlefont=dict(family='Calibri Light'),barmode='group')

    fig.append_trace(trace1,1,1)
    fig.append_trace(trace2,1,1)
    fig.append_trace(trace3,1,2)
    fig.append_trace(trace4,1,2)

    fig.append_trace(trace5,1,3)
    fig.append_trace(trace6,1,3)
    fig.append_trace(trace7,1,4)
    fig.append_trace(trace8,1,4)

    for i in fig['layout']['annotations']:
        i['font'] = dict(family='Calibri Light',size=15)

    fig['layout']['yaxis1'].update(showgrid=False,autorange='reversed')
    return fig

########<Top 15 SKU by country Callbacks>########
@app.callback(
    Output('skubar','figure'),
    [Input('country','value'),
    ]
)

def update_flag(ctry_name):

    SQL="SELECT itemname, salesplkpq, salesplkcq, valplkpq, valplkcq, pricepq, pricecq FROM skubardat WHERE ctry=(%s)"
    cur.execute(SQL,(ctry_name,))
    result=cur.fetchall()
    itemname_val, salesplkpq_val, salesplkcq_val, valplkpq_val, valplkcq_val, pricepq_val, pricecq_val = zip(*result)

    y1=salesplkpq_val
    y2=salesplkcq_val
    y3=valplkpq_val
    y4=valplkcq_val
    y5=pricepq_val
    y6=pricecq_val

    trace1 = go.Bar(x=itemname_val,y=y1,name="Q1",text=salesplkpq_val,textposition = 'auto',marker=dict(color='rgba(0,169,184,1)'))
    trace2 = go.Bar(x=itemname_val,y=y2,name="Q2",text=salesplkcq_val,textposition = 'auto',marker=dict(color='rgba(255,205,42,1)'))

    trace3 = go.Bar(x=itemname_val,y=y3,name="Q1",text=valplkpq_val,textposition = 'auto',marker=dict(color='rgba(0,169,184,1)'),showlegend=False)
    trace4 = go.Bar(x=itemname_val,y=y4,name="Q2",text=valplkcq_val,textposition = 'auto',marker=dict(color='rgba(255,205,42,1)'),showlegend=False)

    trace5 = go.Scatter(x=itemname_val,y=y5,name="Q1 Price USD",text=pricepq_val)
    trace6 = go.Scatter(x=itemname_val,y=y6,name="Q2 Price USD",text=pricecq_val)

    fig = tls.make_subplots(rows=2, cols=1,shared_xaxes=True,subplot_titles=('Sales Volume', 'Sales Value USD'))
    fig['layout']['margin'] = {'l': 100, 'r': 120, 'b': 150, 't': 70}
    # fig['layout']['xaxis'].update(tickfont=dict(size=10))

    fig['layout'].update(title='Top 15 SKUs By Country (Millions) - Q2 2018',titlefont=dict(family='Calibri Light'),barmode='group',hovermode='closest')

    fig.append_trace(trace1,1,1)
    fig.append_trace(trace2,1,1)
    fig.append_trace(trace3,2,1)
    fig.append_trace(trace4,2,1)
    fig.append_trace(trace5,1,1)
    fig.append_trace(trace6,1,1)

    fig['data'][4].update(yaxis='y3')
    fig['data'][5].update(yaxis='y3')
    fig['layout']['yaxis3'] = dict(range=[1, 10], overlaying='y1', anchor='x1', side='right', showgrid=False)

    for i in fig['layout']['annotations']:
        i['font'] = dict(family='Calibri Light',size=16)

    return fig