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

from app import app
from dash.dependencies import Input, Output
from dash import dcc, State, html
from collections import deque
from utils import search_process

# --------------------------
#      Plot variables
# --------------------------

X1 = deque(maxlen=20)
X1.append(0)
X2 = deque(maxlen=20)
X2.append(0)
Y = deque(maxlen=20)
Y.append(0)
Z = deque(maxlen=20)
Z.append(0)


def generate_table(id, data, cols=None):
    if cols:
        table = html.Table(
            id=id,
            className='plot-tables',
            children=
            # Header
            [html.Tr([html.Th(col) for col in cols])] +
            # Body
            [html.Tr([html.Td(k), html.Td(v)]) for k, v in data.items()],
        )
    else:
        table = html.Table(
            id=id,
            className='plot-tables',
            children=[
                html.Tr([html.Td(k), html.Td(v)]) for k, v in data.items()
            ],
        )
    return table


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

    html.Div(
        children=[
            html.Div(
                id='cpu-div',
                className='plot-area',
                children=[
                    dcc.Graph(id='cpu-graph', animate=True),
                    html.Div(id='cpu-table'),
                ],
                style={'width': '48%', 'margin-right': '4%'}
            ),

            html.Div(
                id='mem-div',
                className='plot-area',
                children=[
                    dcc.Graph(id='mem-graph', animate=True),
                    html.Div(id='mem-table'),
                ],
                style={'width': '48%'}
            ),
        ],
        style={'display': 'flex'},
    ),

    # --------------------------
    #      Process Info
    # --------------------------
    html.H3(children='EvalNE process info', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(
        children=[
            html.Div(
                id='proc-div',
                className='plot-area',
                children=[
                    html.Div(id='proc-table'),
                ],
                style={'width': '48%', 'margin-right': '4%'}
            ),

            html.Div(
                id='proc2-div',
                className='plot-area',
                children=[
                    html.Div(id='proc2-table'),
                ],
                style={'width': '48%'}
            ),
        ],
        style={'display': 'flex'},
    ),

    # --------------------------
    #     Evaluation Output
    # --------------------------
    html.H3(children='Latest evaluation output', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div([
        html.Pre(id='console-out', className='bash')
    ])

])


# -------------
#   Callbacks
# -------------

@app.callback(
    Output('console-out', 'children'),
    Input('plot-update-interval', 'n_intervals'))
def update_output(n):
    try:
        filename = os.path.join(os.getcwd(), 'console.out')
        f = open(filename, 'r')
        text = f.read()
        f.close()
        return text.replace('\n', '\nfoo@bar:~$ ')
    except:
        return ''


@app.callback(
    Output('proc-table', 'children'),
    Output('proc2-table', 'children'),
    Input('plot-update-interval', 'n_intervals'))
def update_tables(n):
    p = search_process('evalne')
    proc = {
        'pid': p.pid if p else 'Unknown',
        'name': p.name() if p else 'Unknown',
        'cmdline': ' '.join(p.cmdline()) if p else 'Unknown',
        'status': p.status() if p else 'Unknown',
        'created': p.create_time() if p else 'Unknown',
        'mem_percent': p.memory_percent() if p else 'Unknown',
        'cpu_percent': p.cpu_percent(0) if p else 'Unknown',
    }
    res = [
        generate_table('proc-info', proc, None),
        generate_table('proc2-info', proc, None),
    ]
    return res


@app.callback(
    Output('cpu-table', 'children'),
    Output('mem-table', 'children'),
    Input('plot-update-interval', 'n_intervals'))
def update_tables(n):
    mem = psutil.virtual_memory()
    memlst = [mem.used / (1024*1024*1024), mem.available / (1024*1024*1024), mem.total / (1024*1024*1024)]

    res = [
        generate_table('cpu-info',
                       dict(list(zip(
                           ['Load average (1 min): ', 'Load average (5 min): ', 'Load average (15 min): '],
                           ['{:.2f} %'.format(x / psutil.cpu_count() * 100) for x in psutil.getloadavg()]))),
                       None),
        generate_table('mem-info',
                       dict(list(zip(
                           ['Used Memory (%): ', 'Available Memory (%): ', 'Total Memory (%): '],
                           ['{:.2f} GB'.format(x) for x in memlst]))),
                       None),
    ]
    return res


@app.callback(Output('cpu-graph', 'figure'),
              Input('plot-update-interval', 'n_intervals'))
def update_graph_live1(n):
    X1.append(X1[-1] + 1)
    Y.append(psutil.cpu_percent())

    fig = go.Figure()

    fig.update_xaxes(title_text="", range=[min(X1), max(X1)], showticklabels=False)
    fig.update_yaxes(title_text="", range=[0, 100])

    fig.add_trace({
        'x': list(X1),
        'y': list(Y),
        'name': 'CPU Usage',
        'mode': 'lines',
        'type': 'scatter',
        'fill': 'tozeroy',
        'line_color': 'limegreen'
    })

    fig.update_layout(title='CPU Usage (%)', showlegend=False, autosize=True, height=300,
                      margin={'l': 10, 'r': 10, 'b': 10, 't': 50})

    return fig


@app.callback(Output('mem-graph', 'figure'),
              Input('plot-update-interval', 'n_intervals'))
def update_graph_live2(n):
    X2.append(X1[-1] + 1)
    Z.append(psutil.virtual_memory()[2])

    fig = go.Figure()

    fig.update_xaxes(title_text="", range=[min(X2), max(X2)], showticklabels=False)
    fig.update_yaxes(title_text="", range=[0, 100])

    fig.add_trace({
        'x': list(X2),
        'y': list(Z),
        'name': 'CPU Usage',
        'mode': 'lines',
        'type': 'scatter',
        'fill': 'tozeroy',
        'line_color': 'gold'
    })

    fig.update_layout(title='Memory Usage (%)', showlegend=False, autosize=True, height=300,
                      margin={'l': 10, 'r': 10, 'b': 10, 't': 50})

    return fig
