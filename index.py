import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_auth
from app import app
from apps import shelldashboard,howtouse,notes
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

import plotly
import dash_auth

import plotly.plotly as py
import plotly.graph_objs as go

global myauthenticateduser




app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'  # noqa: E501
    })

app.config['suppress_callback_exceptions']=True
server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')
auth = dash_auth.BasicAuth(
    app,
    (('Retailaudit','Distributionkpis',),('gfkinternal','gfkoneposdb',),('aajaya','gfkoneposdb37',),('APMEGM','conrad',),('APMEREGION','Distributionkpis',),)
)

app.layout = html.Div([
                dcc.Location(id='url',refresh=True),
                html.Div(id='page-content'),
                html.Div(id='shelldbcontent'),
            ],style={'font-family': 'Calibri Light'},className='ten columns offset-by-one')


# myauthenticateduser = auth._username
# shelldb = shelldashboard.layout
# shellhtu = howtouse.layout
# shellnotes = notes.layout

@app.callback(Output('page-content', 'children'),
             [Input('url', 'pathname')]
)
def display_page(pathname):
    shelldb = shelldashboard.layout
    shellhtu = howtouse.layout
    shellnotes = notes.layout
    if pathname == '/apps/shelldashboard':
         return shelldb
    elif pathname == '/apps/howtouse':
         return shellhtu
    elif pathname == '/apps/notes':
         return shellnotes
    else:
         return shelldb


@app.callback(Output('shelldbcontent', 'children'),
              [Input('shelldbtabs', 'value')])

def render_content(tab):
    myauthenticateduser = auth._username
    if myauthenticateduser == 'aajaya' or myauthenticateduser == 'APMEGM' or myauthenticateduser == 'APMEREGION':
        if tab == 'apme':
            return html.Div([
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
                            value='channel_analysis',
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
                                id='country', #Left it is as 'country' since i didnt want to change all the code again. What it really means is region
                                value='APME',
                                options=[
                                    {'label': 'APME Total', 'value': 'APME'},
                                    {'label': 'Oman', 'value': 'Oman'},
                                    {'label': 'Saudi Arabia', 'value': 'Saudi Arabia'},
                                    {'label': 'United Arab Emirates', 'value': 'United Arab Emirates'},
                                    {'label': 'Egypt', 'value': 'Egypt'},
                                    # {'label': 'APAC Total', 'value': 'APAC'},
                                    {'label': 'Indonesia', 'value': 'Indonesia'},
                                    {'label': 'Thailand', 'value': 'Thailand'},
                                    {'label': 'Malaysia', 'value': 'Malaysia'},
                                ],
                                placeholder="Country",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Engine Oil Type:'),
                            dcc.Dropdown(
                                id='typeveh',
                                value='TOTAL',
                                placeholder="Type Of Vehicle",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Region:'),
                            dcc.Dropdown(
                                id='region',
                                value='TOTAL',
                                placeholder="Region",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Channel:'),
                            dcc.Dropdown(
                                id='channel',
                                value='TOTAL',
                                placeholder="Channel",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Subgroup:'),
                            dcc.Dropdown(
                                id='base',
                                value='TOTAL',
                                placeholder="Base",
                            ),
                        ],className='two columns')
                    ],className='row'),
                    html.Br(),

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
                    dcc.Markdown('''---'''),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='distbrand',
                                config={'displayModeBar': False}
                            ),
                        ],className='row'),
                    ]),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '500px'},
                            id='pothead',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                    html.Div([
                        html.P('- Please refer to point (2) under the notes tab for more details on the graph')
                    ],className='nine columns', style= {'display': 'inline-block'}),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '900px'},
                            id='skubar',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                ],style={'font-family': 'Calibri Light'})

    if myauthenticateduser == 'Retailaudit' or myauthenticateduser == 'gfkinternal':
        if tab == 'global':
            return html.Div([
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
                            value='channel_analysis',
                            labelStyle={'display': 'inline-block'}
                        ),
                        html.Div([
                            html.P('Note: Selecting an option will disable the other. For example, selecting By Region will disable Select Channel dropdown')
                        ],className='nine columns', style= {'display': 'inline-block','color': 'red'}),
                    ],className='row',style={'display': 'none'}),
                    html.Br(),
                    html.Div([
                        dcc.Dropdown(
                            id='country',
                            value='Global',
                        )
                    ],style={'display': 'none'}),
                    html.Div([
                        html.Div([
                            html.P('Select Engine Oil Type:'),
                            dcc.Dropdown(
                                id='typeveh',
                                value='TOTAL',
                                placeholder="Type Of Vehicle",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Region:'),
                            dcc.Dropdown(
                                id='region',
                                value='TOTAL',
                                placeholder="Region",
                            ),
                        ],className='two columns',style={'display': 'none'}),

                        html.Div([
                            html.P('Select Channel:'),
                            dcc.Dropdown(
                                id='channel',
                                value='TOTAL',
                                placeholder="Channel",
                            ),
                        ],className='two columns',style={'display': 'none'}),

                        html.Div([
                            html.P('Select Subgroup:'),
                            dcc.Dropdown(
                                id='base',
                                value='TOTAL',
                                placeholder="Base",
                            ),
                        ],className='two columns')
                    ],className='row'),
                    html.Br(),

                    #QoQ Brandshares Div


                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='brandshares5',
                                config={'displayModeBar': False},
                            )
                        ],className='six columns'),
                        html.Div([
                            dcc.Graph(
                                id='brandshares6',
                                config={'displayModeBar': False},
                            )
                        ],className='six columns')
                    ],className='row'),

                    #YoY Brandshares Div
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='brandshares9',
                                config={'displayModeBar': False},
                            )
                        ],className='six columns'),
                        html.Div([
                            dcc.Graph(
                                id='brandshares8',
                                config={'displayModeBar': False},
                            )
                        ],className='six columns')
                    ],className='row'),
                    dcc.Markdown('''---'''),

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
                    dcc.Markdown('''---'''),

                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='pie',
                                config={'displayModeBar': False}
                            ),
                        ],className='row'),
                    ]),
                    dcc.Markdown('''---'''),

                    html.Div([
                        html.Div([
                            dcc.Graph(
                                style={'height': '1200px'},
                                id='horizbar',
                                config={'displayModeBar': False}
                            ),
                        ],className='row'),
                    ]),
                ],style={'font-family': 'Calibri Light'})
        if tab == 'apme':
            return html.Div([
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
                            value='channel_analysis',
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
                                id='country', #Left it is as country since i didnt want to change all the code again. What it really means is region
                                value='MENA',
                                options=[
                                    {'label': 'APME Total', 'value': 'APME'},
                                    {'label': 'Oman', 'value': 'Oman'},
                                    {'label': 'Saudi Arabia', 'value': 'Saudi Arabia'},
                                    {'label': 'United Arab Emirates', 'value': 'United Arab Emirates'},
                                    {'label': 'Egypt', 'value': 'Egypt'},
                                    # {'label': 'APAC Total', 'value': 'APAC'},
                                    {'label': 'Indonesia', 'value': 'Indonesia'},
                                    {'label': 'Thailand', 'value': 'Thailand'},
                                    {'label': 'Malaysia', 'value': 'Malaysia'},
                                ],
                                placeholder="Country",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Engine Oil Type:'),
                            dcc.Dropdown(
                                id='typeveh',
                                value='TOTAL',
                                placeholder="Type Of Vehicle",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Region:'),
                            dcc.Dropdown(
                                id='region',
                                value='TOTAL',
                                placeholder="Region",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Channel:'),
                            dcc.Dropdown(
                                id='channel',
                                value='TOTAL',
                                placeholder="Channel",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Subgroup:'),
                            dcc.Dropdown(
                                id='base',
                                value='TOTAL',
                                placeholder="Base",
                            ),
                        ],className='two columns')
                    ],className='row'),
                    html.Br(),

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
                    dcc.Markdown('''---'''),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='distbrand',
                                config={'displayModeBar': False}
                            ),
                        ],className='row'),
                    ]),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '500px'},
                            id='pothead',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                    html.Div([
                        html.P('- Please refer to point (2) under the notes tab for more details on the graph')
                    ],className='nine columns', style= {'display': 'inline-block'}),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '900px'},
                            id='skubar',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                ],style={'font-family': 'Calibri Light'})
        if tab == 'russia':
            return html.Div([
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
                            value='region_analysis',
                            labelStyle={'display': 'inline-block'}
                        ),
                        html.Div([
                            html.P('Note: Selecting an option will disable the other. For example, selecting By Region will disable Select Channel dropdown')
                        ],className='nine columns', style= {'display': 'inline-block','color': 'red'}),
                    ],className='row'),
                    html.Br(),
                    html.Div([
                        dcc.Dropdown(
                            id='country',
                            value='Russia',
                        )
                    ],style={'display': 'none'}),
                    html.Div([
                        html.Div([
                            html.P('Select Engine Oil Type:'),
                            dcc.Dropdown(
                                id='typeveh',
                                value='TOTAL',
                                placeholder="Type Of Vehicle",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Region:'),
                            dcc.Dropdown(
                                id='region',
                                value='TOTAL',
                                placeholder="Region",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Channel:'),
                            dcc.Dropdown(
                                id='channel',
                                value='TOTAL',
                                placeholder="Channel",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Subgroup:'),
                            dcc.Dropdown(
                                id='base',
                                value='TOTAL',
                                placeholder="Base",
                            ),
                        ],className='two columns')
                    ],className='row'),
                    html.Br(),

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
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            id='distbrand',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '500px'},
                            id='pothead',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                    html.Div([
                        html.P('- Please refer to point (2) under the notes tab for more details on the graph')
                    ],className='nine columns', style= {'display': 'inline-block'}),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '900px'},
                            id='skubar',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                ],style={'font-family': 'Calibri Light'})

        if tab == 'china':
            return html.Div([
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
                            value='channel_analysis',
                            labelStyle={'display': 'inline-block'}
                        ),
                        html.Div([
                            html.P('Note: Selecting an option will disable the other. For example, selecting By Region will disable Select Channel dropdown')
                        ],className='nine columns', style= {'display': 'inline-block','color': 'red'}),
                    ],className='row'),
                    html.Br(),
                    html.Div([
                        dcc.Dropdown(
                            id='country',
                            value='China',
                        )
                    ],style={'display': 'none'}),
                    html.Div([
                        html.Div([
                            html.P('Select Engine Oil Type:'),
                            dcc.Dropdown(
                                id='typeveh',
                                value='TOTAL',
                                placeholder="Type Of Vehicle",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Region:'),
                            dcc.Dropdown(
                                id='region',
                                value='TOTAL',
                                placeholder="Region",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Channel:'),
                            dcc.Dropdown(
                                id='channel',
                                value='TOTAL',
                                placeholder="Channel",
                            ),
                        ],className='two columns'),

                        html.Div([
                            html.P('Select Subgroup:'),
                            dcc.Dropdown(
                                id='base',
                                value='TOTAL',
                                placeholder="Base",
                            ),
                        ],className='two columns')
                    ],className='row'),
                    html.Br(),

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
                    dcc.Markdown('''---'''),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='distbrand',
                                config={'displayModeBar': False}
                            ),
                        ],className='row'),
                    ]),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '500px'},
                            id='pothead',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                    html.Div([
                        html.P('- Please refer to point (2) under the notes tab for more details on the graph')
                    ],className='nine columns', style= {'display': 'inline-block'}),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    dcc.Markdown('''---'''),
                    html.Div([
                        dcc.Graph(
                            style={'height': '900px'},
                            id='skubar',
                            config={'displayModeBar': False}
                        ),
                    ],className='row'),
                ],style={'font-family': 'Calibri Light'})


if __name__ == '__main__':
    app.run_server(debug=True)
