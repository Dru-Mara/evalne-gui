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
from evalne_gui.utils import get_logged_evals


runs_layout = html.Div([

    dcc.Interval(
        id='runs-update-interval',
        interval=5*1000,    # in milliseconds
        n_intervals=0
    ),

    html.H3(children='Logged Evaluation Runs', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(
        id='logged-eval-div',
        className='plot-area',
        children=[
            html.Div(id='logged-eval-table'),
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

@app.callback(Output('logged-eval-table', 'children'),
              Input('runs-update-interval', 'n_intervals'),
              State('settings-data', 'data'))
def update_table(n, settings_data):
    """ Updates the `Runs` table. """

    # Table header
    cols = ['Filename', 'Status', 'Runtime', 'Start Time', 'End Time']

    # Read eval_path from settings and get the evaluations logged there
    settings_data = json.loads(settings_data)
    if settings_data[1] == '':
        eval_path = os.getcwd()
    else:
        eval_path = settings_data[1]
    rows = get_logged_evals(eval_path)

    table = html.Table(
        id='table',
        className='runs-table',
        children=
        # Header
        [html.Tr([html.Th(col) for col in cols])] +
        # Body
        [html.Tr([html.Td(v) for v in row]) for row in rows],
    )

    return table
