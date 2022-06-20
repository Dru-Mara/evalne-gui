#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021

import os
import json

from evalne_gui.app import app
from dash.dependencies import Input, Output
from dash import dcc, State, html
from evalne_gui.utils import get_logged_evals, read_file
from evalne_gui.init_values import *


results_layout = html.Div([

    dcc.Interval(
        id='res-update-interval',
        interval=5*1000,    # in milliseconds
        n_intervals=0
    ),

    html.H3(children='Evaluation Runs and Results', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(
        id='eval-tabs-div',
        className='plot-area',
        children=[
            html.Div(id='eval-tabs-table'),
        ],
    ),

    # --------------------------
    #       Data storage
    # --------------------------
    dcc.Store(id='settings-data', storage_type='local'),

])


# --------------------------
#         Callbacks
# --------------------------

@app.callback(Output('eval-tabs-table', 'children'),
              Input('res-update-interval', 'n_intervals'),
              State('settings-data', 'data'))
def update_table(n, settings_data):
    """ Updates the `Runs and Results` table. """

    # Table header
    cols = ['Filename', 'Status', 'Runtime', 'Start Time', 'End Time']

    # Read eval_path from settings and get the evaluations logged there
    if settings_data is None:
        settings_data = [val for val in init_settings.values()]
    else:
        settings_data = json.loads(settings_data)
    if settings_data[1] == '':
        eval_path = os.getcwd()
    else:
        eval_path = settings_data[1]
    try:
        rows = get_logged_evals(eval_path)
    except FileNotFoundError:
        rows = []

    # Present evaluations as rows in a table
    table = [
        html.Table(
            children=[
                html.Tr(
                    children=[
                        html.Th(col) for col in cols
                    ],
                    style={'border-top': 'hidden'},
                )
            ],
            style={'width': '100%', 'display': 'inline-table'}
        )
    ]

    # Dash Tables cannot have expandable rows, so workaround having each row be a table in itself
    table += [
        html.Details(
            children=[
                html.Summary(
                    children=[
                        html.Table(
                            children=[
                                html.Tr(
                                    children=[
                                        html.Td(v) for v in row
                                    ],
                                    style={'border-top': 'hidden'}
                                )
                            ],
                            style={'width': '100%', 'display': 'inline-table'}
                        )
                    ],
                    style={'display': 'flex'}
                ),
                # Hidden content
                html.Div(
                    children=[
                        html.H4(['Evaluation Log']),
                        html.Pre(id='log-out', className='bash', children=read_file(os.path.join(eval_path, row[0]),
                                                                                    'eval.log')),
                        html.Br(),
                        html.Br(),
                        html.H4(['Evaluation Results']),
                        html.Pre(id='res-out', className='bash', children=read_file(os.path.join(eval_path, row[0]),
                                                                                    'eval_output.txt')),
                        html.Br(),
                        html.Br(),
                    ],
                    style={'margin-left': '10%', 'margin-right': '10%'}
                )
            ],
            open=False,
        ) for row in rows]

    return table
