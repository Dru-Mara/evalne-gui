#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021

import os
import sys
import json

from evalne_gui.app import app
from dash import callback_context
from dash import dcc, State, html
from dash.dependencies import Input, Output
from evalne_gui.init_values import *


settings_layout = html.Div([

    # --------------------------
    #          Buttons
    # --------------------------
    html.Br(),
    html.Br(),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Button('Reset Default', id='set-default', className='btn btn-square btn-imp', n_clicks=0),
                ]
            ),
        ],
        style={'display': 'flex', 'float': 'right'}
    ),
    html.Br(),
    html.Br(),

    # --------------------------
    #      Global settings
    # --------------------------
    html.H3(children='Global Settings', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    # Settings for python path and evaluation folder
    html.Div(
        className='plot-area',
        children=[
            html.Div(
                children=[
                    html.Label(['Set EvalNE Python path:']),
                    dcc.Input(id="ib-pythonpath", className='input-box', type="text", value=init_settings['ib-pythonpath'],
                              placeholder="Insert path to python executable where EvalNE is installed. Default is: `{}`"
                              .format(sys.executable), persistence=True),
                ],
            ),
            html.Br(),
            html.Div(
                children=[
                    html.Label(['Set evaluation folder path:']),
                    dcc.Input(id="ib-evalpath", className='input-box', type="text", value=init_settings['ib-evalpath'],
                              placeholder="Insert path to folder where to store results. Default is: `{}`"
                              .format(os.getcwd()), persistence=True),
                ],
            ),
            html.Br(),
        ]
    ),

    # --------------------------
    #       Data storage
    # --------------------------
    dcc.Store(id='settings-data', storage_type='local'),
])


# --------------------------
#         Callbacks
# --------------------------

@app.callback([[Output(key, 'value') for key in init_settings.keys()]],
              Output('settings-data', 'data'),
              [[Input(key, 'value') for key in init_settings.keys()]],
              Input('set-default', 'n_clicks'),
              State('settings-data', 'data'))
def refresh_config(data, nclick, old_data):
    """ This function stores and loads settings from a dcc.Store on page-refresh/tab-change/user-action. """

    ctx = callback_context

    if not ctx.triggered:
        if old_data is None:
            # Triggered on first ui load
            res = [val for val in init_settings.values()]
            return res, json.dumps(res)
        else:
            # Triggered when changing tabs/restarting
            od = json.loads(old_data)
            return od, old_data
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'set-default':
            # Triggered by user click
            res = [val for val in init_settings.values()]
            return res, json.dumps(res)
        else:
            # Triggered when any value is changed in conf
            return data, json.dumps(data)
