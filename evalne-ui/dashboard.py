import os
import dash
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from dash import dcc, State, html
from dash.html.Label import Label


dashboard_layout = html.Div([

    html.H3(children='Global and Edge Sampling Parameters'),
    html.Hr(),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label(['Evaluation Task:']),
                    dcc.Dropdown(
                        id='task-dropdown',
                        options=[{'label': 'Link prediction', 'value': 'LP'},
                                 {'label': 'Sign prediction', 'value': 'SP'},
                                 {'label': 'Network reconstruction', 'value': 'NR'},
                                 {'label': 'Node classification', 'value': 'NC'}],
                        value='LP',
                    ),
                ],
                style={'width': '30%', 'padding-right': '3%'}
            ),
            html.Div(
                children=[
                    html.Label(['Num Edge Splits:']),
                    dcc.Input(id="input-box-1", type="number", value=5, style={'height': '30px'}),
                ],
                style={'width': '30%', 'padding-right': '3%'}
            ),
            html.Div(
                children=[
                    html.Label(['Edge Embedding Method:']),
                    dcc.Dropdown(
                        id='ee-dropdown',
                        options=[{'label': 'Average', 'value': 'Avg'},
                                 {'label': 'Hadamard', 'value': 'Had'},
                                 {'label': 'Weighted L1', 'value': 'WL1'},
                                 {'label': 'Weighted L2', 'value': 'WL2'}],
                        value='Avg',
                    ),
                ],
                style={'width': '30%', 'padding-right': '3%'}
            ),
        ],
        style={'display': 'flex'}
    ),


    # TASK (dropdown)
        # if LP:
            # LP_NUM_EDGE_SPLITS (text check integer)
            # EDGE_EMBEDDING_METHODS (dropdown)
        # if NR
            # NR_EDGE_SAMP_FRAC (text check integer)
            # EDGE_EMBEDDING_METHODS (dropdown)
        # if NC
            # NC_NUM_NODE_SPLITS (text check integer)
            # NC_NODE_FRACS (text check frac)
    # LP_MODEL (dropdown + custom input)
    # EMBED_DIM (text check integer)
    # TIMEOUT (text check integer)
    # SEED (text check integer)
    # VERBOSE (checkbox)

    # TRAINTEST_FRAC (text check frac)
    # TRAINVALID_FRAC (text check frac)
    # SPLIT_ALG (dropdown)
    # OWA (dropdown)
    # FE_RATIO (text check integer)

    html.H3(children='Networks and Preprocessing'),
    # NAMES (text)
    # INPATHS (text)
    # LABELPATH (text)
    # DIRECTED (checkbox)
    # SEPARATORS (dropdown + custom input)
    # COMMENTS (dropdown + custom input)

    # RELABEL (checkbox)
    # DEL_SELFLOOPS (checkbox)
    # SAVE_PREP_NW (checkbox)
    # WRITE_STATS (checkbox)
    # DELIMITER (dropdown + custom input)

    html.H3(children='Baselines and NE methods'),

    html.H3(children='Metrics and Plots'),
    # MAXIMIZE (dropdown)
    # SCORES (dropdown)
    # CURVES (dropdown)
    # PRECATK_VALS (text??)


    dcc.Dropdown(
        id='page-1-dropdown',
        options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        value='LA'
    ),
    html.Div(id='page-1-content'),
    html.Br(),

])




