#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021

import os
import json
import psutil
import plotly.graph_objects as go

from evalne_gui.app import app
from dash.dependencies import Input, Output
from dash import dcc, State, html
from collections import deque
from evalne_gui.utils import get_ui_proc, get_evalne_proc, read_file
from evalne_gui.init_values import *


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


def generate_table(tblid, data, cols=None, title=None):
    table = []
    if title:
        table = [html.Center([html.H4([title])])]
    if cols:
        table.append(html.Table(
            id=tblid,
            className='plot-tables',
            children=
            # Header
            [html.Tr([html.Th(col) for col in cols])] +
            # Body
            [html.Tr([html.Td(k), html.Td(v)]) for k, v in data.items()],
        ))
    else:
        table.append(html.Table(
            id=tblid,
            className='plot-tables',
            children=[
                html.Tr([html.Td(k), html.Td(v)]) for k, v in data.items()
            ],
        ))
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
    html.H3(children='System Resource Monitoring', className='section-title'),
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
    html.H3(children='Process Info', className='section-title'),
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
    html.H3(children='Latest Evaluation Output', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(
        children=[
            html.Pre(id='console-out', className='bash')
        ],
        style={'margin': '10px 30px 30px 30px'},
    ),

    # --------------------------
    #       Data storage
    # --------------------------
    dcc.Store(id='settings-data', storage_type='local'),

])


# --------------------------
#         Callbacks
# --------------------------

@app.callback(Output('cpu-graph', 'figure'),
              Input('plot-update-interval', 'n_intervals'))
def update_graph_live1(n):
    """ Periodically updates the CPU usage graph. """

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
    """ Periodically updates the RAM usage graph. """

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


@app.callback(
    Output('cpu-table', 'children'),
    Output('mem-table', 'children'),
    Input('plot-update-interval', 'n_intervals'))
def update_tables(n):
    """ Periodically updates the info shown in the tables under each plot. """

    mem = psutil.virtual_memory()
    memlst = [mem.used / (1024 * 1024 * 1024), mem.available / (1024 * 1024 * 1024), mem.total / (1024 * 1024 * 1024)]

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


@app.callback(
    Output('proc-table', 'children'),
    Output('proc2-table', 'children'),
    Input('plot-update-interval', 'n_intervals'))
def update_tables(n):
    """ Periodically updates the EvalNE-UI and EvalNE proc info tables. """

    # Get process info for the tables
    ui_proc_info = get_ui_proc().info()
    evalne_proc_info = get_evalne_proc().info()

    return [
        generate_table('proc-info', ui_proc_info, None, 'EvalNE-UI Process Info'),
        generate_table('proc2-info', evalne_proc_info, None, 'EvalNE Process Info'),
    ]


@app.callback(
    Output('console-out', 'children'),
    Input('plot-update-interval', 'n_intervals'),
    State('settings-data', 'data'))
def update_output(n, settings_data):
    """ Periodically updates the evaluation output section by reading a `console.out` file. """

    if settings_data is None:
        settings_data = [val for val in init_settings.values()]
    else:
        settings_data = json.loads(settings_data)
    if settings_data[1] == '':
        eval_path = os.getcwd()
    else:
        eval_path = settings_data[1]
    text = read_file(eval_path, 'console.out', console=True)
    return text.replace('\n', '\nfoo@bar:~$ ')
