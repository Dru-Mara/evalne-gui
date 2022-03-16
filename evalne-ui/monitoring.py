import os
import dash
import time
import psutil
import plotly
import socket
import platform
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd
import datetime
import logging

from app import app, dashLoggerHandler
from dash.dependencies import Input, Output
from dash import dcc, State, html
from collections import deque

X = deque(maxlen=20)
X.append(0)

Xl = deque(maxlen=20)
Xl.append(datetime.datetime.now().strftime("%H:%M:%S"))

Y = deque(maxlen=20)
Y.append(0)

Z = deque(maxlen=20)
Z.append(0)

monitoring_layout = html.Div([

    dcc.Interval(
        id='plot-update-interval',
        interval=1*1000,    # in milliseconds
        n_intervals=0
    ),

    # --------------------------
    #      Global settings
    # --------------------------
    html.H3(children='System resource monitoring', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(id='graphs12', className='plot-area', children=[
        dcc.Graph(id='live-update-graph', animate=True),
    ]),

    # --------------------------
    #      Process Info
    # --------------------------
    html.H3(children='EvalNE process info', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    # TODO

    # --------------------------
    #     Evaluation Output
    # --------------------------
    html.H3(children='Evaluation output', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(id='output', className='plot-area', children=[
        html.Iframe(id='console-out', srcDoc='', style={'width': '100%', 'height':400})
    ])

])


# -------------
#   Callbacks
# -------------

@app.callback(
    Output('console-out', 'srcDoc'),
    Input('plot-update-interval', 'n_intervals'))
def update_output(n):
    logging.info('working')
    return ('\n'.join(dashLoggerHandler.queue)).replace('\n', '<BR>')


@app.callback(Output('live-update-graph', 'figure'),
              Input('plot-update-interval', 'n_intervals'))
def update_graph_live(n):
    X.append(X[-1] + 1)
    Xl.append(datetime.datetime.now().strftime("%H:%M:%S"))
    Y.append(psutil.cpu_percent())
    Z.append(psutil.virtual_memory()[2])

    # Create the graph with subplots
    fig = plotly.subplots.make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5],
                                        subplot_titles=('CPU Usage (%)', 'Memory Usage (%)'))

    fig.update_xaxes(title_text="", range=[min(X), max(X)], row=1, col=1, showticklabels=False)
    fig.update_xaxes(title_text="", range=[min(X), max(X)], row=1, col=2, showticklabels=False)

    fig.update_yaxes(title_text="", range=[0, 100], row=1, col=1)
    fig.update_yaxes(title_text="", range=[0, 100], row=1, col=2)

    fig.add_trace({
        'x': list(X),
        'y': list(Y),
        'name': 'CPU Usage',
        'mode': 'lines',
        'type': 'scatter',
        'fill': 'tozeroy',
        'line_color': 'limegreen'
    }, 1, 1)
    fig.add_trace({
        'x': list(X),
        'y': list(Z),
        'name': 'Virtual Memory Usage',
        'mode': 'lines',
        'type': 'scatter',
        'fill': 'tozeroy',
        'line_color': 'gold'       # 'line': dict(width=1.5, color='rgb(0, 255, 0)')
    }, 1, 2)

    fig.update_layout(height=300, showlegend=False, margin={'l': 30, 'r': 10, 'b': 30, 't': 10})

    return fig

