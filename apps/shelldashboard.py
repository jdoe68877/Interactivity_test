import os
import pickle
import copy
import psycopg2
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.tools as tls
from io import StringIO
import numpy as np
import plotly
import dash_auth

import plotly.plotly as py
import plotly.graph_objs as go

from app import app

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'font-family': 'Calibri Light',
    'color': '#FF8C00',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '3px solid #d6d6d6',
    'borderBottom': '0px solid #d6d6d6',
    'backgroundColor': '#FF8C00',
    'color': 'white',
    'padding': '6px',
    'fontWeight': 'bold',
    'font-family': 'Calibri Light'
}

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501

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
        dcc.Location(
             id='url1'
        ),

        dcc.Location(
             id='url2'
        ),

        html.Div([
            html.Div([
                html.H1(
                    'GfK ONE - POS DASHBOARD',
                    className='five columns',
                )
            ],style={'color': '#FF8C00'}),

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
        ],className='row'),

        html.Br(),
        html.Div([
            html.Button('How To Use', id='button1', style={'width':'180px','color': '#FF8C00','fontWeight': 'bold','font-family': 'Calibri Light','fontSize':'14'}, className='one column'),
            html.Button('Notes', id='button2', style={'width':'180px','color': '#FF8C00','fontWeight': 'bold','font-family': 'Calibri Light','fontSize':'14'}, className='one column'),
        ],className='row'),


        dcc.Markdown('''---'''),

        dcc.Tabs(id='shelldbtabs', value='global', children=[
            dcc.Tab(label='GLOBAL', value='global', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='APME', value='apme', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='RUSSIA', value='russia', style=tab_style, selected_style=tab_selected_style),
            # dcc.Tab(label='APAC', value='apac', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='CHINA (data updated till 2018)', value='china', style=tab_style, selected_style=tab_selected_style),
            # dcc.Tab(label='EU', value='eu', style=tab_style, selected_style=tab_selected_style)
        ]),
        html.Br(),


    ]
)

auth = 'retailaudit'

@app.callback(Output('url1', 'pathname'),
              [Input('button1', 'n_clicks')])

def render_content1(clickData):
    if clickData > 0:
        return '/apps/howtouse'

@app.callback(Output('url2', 'pathname'),
              [Input('button2', 'n_clicks')])

def render_content2(clickData2):
    if clickData2 > 0:
        return '/apps/notes'



########<Options for dropdowns Callbacks>########
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

########<CHARTS>########

########<Brand Share Chart Callbacks - Top Brands>########

#QoQ Chart Callback
@app.callback(
    Output('brandshares5','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
     ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, salesplkpq, salesplkcq FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, salesplkpq, salesplkcq FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, salesplkpq_val, salesplkcq_val = zip(*result)
    trial_y=brand_val
    periods=['Q1 2019','Q2 2019']
    trial_x1=salesplkpq_val
    trial_x2=salesplkcq_val

    m=len(brand_val)
    print(m)

    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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
        title='Statistically Modified Volume Share Q-o-Q',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig


@app.callback(
    Output('brandshares6','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
     ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):


    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, valplkpq, valplkcq FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, valplkpq, valplkcq FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, valplkpq_val, valplkcq_val = zip(*result)

    trial_y=brand_val
    periods=['Q1 2019','Q2 2019']

    trial_x3=valplkpq_val
    trial_x4=valplkcq_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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
        title='Statistically Modified Value Share Q-o-Q (USD)',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig

#YoY Chart Callback
@app.callback(
    Output('brandshares9','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
    ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, salesplkpy, salesplkcy FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, salesplkpy, salesplkcy FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, salesplkpy_val, salesplkcy_val = zip(*result)

    trial_y=brand_val
    periods=['FY 2018','FY 2019']
    trial_x1=salesplkpy_val
    trial_x2=salesplkcy_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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
        title='Statistically Modified Volume Share Y-o-Y (FY 2019)',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig

@app.callback(
    Output('brandshares8','figure'),
    [Input('analysistype','value'),
     Input('country','value'),
     Input('typeveh','value'),
     Input('region','value'),
     Input('channel','value'),
     Input('base','value')
    ]
)

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, valplkpy, valplkcy FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, valplkpy, valplkcy FROM statmodshare WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, valplkpy_val, valplkcy_val = zip(*result)

    trial_y=brand_val
    periods=['FY 2018','FY 2019']

    trial_x3=valplkpy_val
    trial_x4=valplkcy_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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
        title='Statistically Modified Value Share Y-o-Y (FY 2019)(USD)',        # set plot title
        showlegend=True,   # remove legend
        hovermode='closest',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig

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

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, salesplkpq, salesplkcq FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, salesplkpq, salesplkcq FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, salesplkpq_val, salesplkcq_val = zip(*result)
    trial_y=brand_val
    periods=['Q1 2019','Q2 2019']
    trial_x1=salesplkpq_val
    trial_x2=salesplkcq_val

    m=len(brand_val)
    print(m)

    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):


    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, valplkpq, valplkcq FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, valplkpq, valplkcq FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, valplkpq_val, valplkcq_val = zip(*result)

    trial_y=brand_val
    periods=['Q1 2019','Q2 2019']

    trial_x3=valplkpq_val
    trial_x4=valplkcq_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, salesplkpy, salesplkcy FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, salesplkpy, salesplkcy FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, salesplkpy_val, salesplkcy_val = zip(*result)

    trial_y=brand_val
    periods=['FY 2018','FY 2019']
    trial_x1=salesplkpy_val
    trial_x2=salesplkcy_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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
        title='Brand Volume Share Y-o-Y (FY 2019)',        # set plot title
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

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT  brands, valplkpy, valplkcy FROM brandshares_region WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,region_name,base_name,))
    elif analysistype_val=='channel_analysis':
        SQL="SELECT  brands, valplkpy, valplkcy FROM brandshares_channel WHERE ctry=(%s) AND typeveh=(%s) AND channel=(%s) AND base=(%s)"
        cur.execute(SQL,(country_name,typeveh_name,channel_name,base_name,))

    result=cur.fetchall()
    brand_val, valplkpy_val, valplkcy_val = zip(*result)

    trial_y=brand_val
    periods=['FY 2018','FY 2019']

    trial_x3=valplkpy_val
    trial_x4=valplkcy_val

    m=len(brand_val)
    print(m)


    def make_trace(x, name):
        if name=='SHELL':
            color1='rgb(255, 213, 0)'
        elif name=='ADNOC':
            color1='rgb(0, 102, 203)'
        elif name=='MOBIL':
            color1='rgb(225, 129, 129)'
        elif name=='TOTAL':
            color1='rgb(84, 84, 169)'
        elif name=='CALTEX':
            color1='rgb(1, 129, 129)'
        elif name=='ENOC':
            color1='rgb(135, 8, 135)'
        elif name=='TOYOTA':
            color1='rgb(160, 212, 255)'
        elif name=='CASTROL':
            color1='rgb(255, 0, 0)'
        elif name=='LEXUS':
            color1='rgb(246, 202, 154)'
        elif name=='ZIC':
            color1='rgb(6, 204, 104)'
        elif name=='AC DELCO':
            color1='rgb(133, 47, 226)'
        elif name=='VOLVO':
            color1='rgb(247, 189, 155)'
        elif name=='VALVOLINE':
            color1='rgb(135, 135, 7)'
        elif name=='GULF':
            color1='rgb(2, 255, 2)'
        elif name=='AXCL':
            color1='rgb(0, 0, 255)'
        elif name=='NISSAN':
            color1='rgb(248, 191, 157)'
        elif name=='<Others>':
            color1='rgb(134, 136, 138)'
        else:
            color1='nomatch'

        if color1=='nomatch':
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                            # set bar colors
                    line= go.Line(
                        color='white',  # set bar border color
                        width=1         # set bar border width
                    )
                ),
                width = 0.3
            )
        else:
            return go.Bar(
                x=periods,   # cities name on the y-axis
                y=x,        # monthly total on x-axis
                name=name,
                text=x,
                hoverinfo='text',
                textposition = 'inside',  # label for hover
                orientation='v', # (!) for horizontal bars, default is 'v'



                marker= go.Marker(
                    color=color1,        # set bar colors
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
        title='Brand Value Share Y-o-Y (FY 2019)(USD)',        # set plot title
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

def update_BS_brands(analysistype_val,country_name, typeveh_name, region_name, channel_name, base_name):

    if analysistype_val=='region_analysis':
        SQL="SELECT brands, wdpq, wdcq, uwdpq, uwdcq FROM distbrand_region4 WHERE ctry=(%s) AND typeveh=(%s) AND region=(%s) AND base=(%s)"
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
    [Input('country','value'),
     Input('typeveh','value'),
     Input('base','value')
    ]
)

def update_BS_brands(globalregion_name, typeveh_name, base_name):

    SQL="SELECT ctry, salesplkq2, valplkq2 FROM pieandbar WHERE globalreg=(%s) AND typeveh=(%s) AND base=(%s)"
    cur.execute(SQL,(globalregion_name,typeveh_name,base_name,))
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
            'title':'Country Panel Split Q2 2019 (Volume% & Value%)',
        }
    }
    return fig

########<Horizontal Bar Charts Callbacks>########
@app.callback(
    Output('horizbar','figure'),
    [Input('country','value'),
     Input('typeveh','value'),
     Input('base','value')
    ]
)

def update_flag(globalregion_name, typeveh_name, base_name):

    SQL="SELECT ctry, salesplkq1, salesplkq2, shellsalesplkq1, shellsalesplkq2, valplkq1, valplkq2, shellvalplkq1, shellvalplkq2 FROM pieandbar WHERE globalreg=(%s) AND typeveh=(%s) AND base=(%s)"
    cur.execute(SQL,(globalregion_name,typeveh_name,base_name,))
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
    fig['layout']['margin'] = {'l': 150, 'r': 20, 'b': 150, 't': 70}

    fig['layout'].update(title='Absolute Panel Volume & Value Figures (Millions) - Q1 2019 vs Q2 2019',titlefont=dict(family='Calibri Light'),barmode='group')

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
    fig['layout']['margin'] = {'l': 100, 'r': 120, 'b': 250, 't': 70}

    fig['layout'].update(title='Top 15 SKUs By Country (Millions) - Q2 2019',titlefont=dict(family='Calibri Light'),barmode='group',hovermode='closest')

    fig.append_trace(trace1,1,1)
    fig.append_trace(trace2,1,1)
    fig.append_trace(trace3,2,1)
    fig.append_trace(trace4,2,1)
    fig.append_trace(trace5,1,1)
    fig.append_trace(trace6,1,1)

    fig['data'][4].update(yaxis='y3')
    fig['data'][5].update(yaxis='y3')
    fig['layout']['yaxis3'] = dict(overlaying='y1', anchor='x1', side='right', showgrid=False)

    for i in fig['layout']['annotations']:
        i['font'] = dict(family='Calibri Light',size=16)

    return fig

########<Potential Headroom Charts Callbacks>########
@app.callback(
    Output('pothead','figure'),
    [Input('country','value'),
     Input('typeveh','value'),
     Input('base','value')
    ]
)

def update_flag(ctry_name, typeveh_name, base_name):

    SQL="SELECT itemname, salesplk, pohplk FROM potheadbar WHERE ctry=(%s) AND typeveh=(%s) AND base=(%s)"
    cur.execute(SQL,(ctry_name,typeveh_name,base_name,))
    result=cur.fetchall()
    item_val, salesplk_val, pohplk_val = zip(*result)

    trial_y=item_val

    trace1 = go.Bar(y=item_val,x=salesplk_val,name='Current market share',orientation = 'h')
    trace2 = go.Bar(y=item_val,x=pohplk_val,name='incremental headroom',orientation = 'h')

    data = [trace1, trace2]
    layout = go.Layout(
        title='Potential Headroom',
        barmode='stack',
        margin=go.layout.Margin(
            l=350,
            r=50,
            b=100,
            t=100,
            pad=4
        ),
        xaxis=go.layout.XAxis(
            tickformat=".2%"
        )
    )

    fig = go.Figure(data=data, layout=layout)
    return fig
