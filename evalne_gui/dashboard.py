#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021

import os
import sys
import json
import dash_bootstrap_components as dbc

from datetime import datetime
from evalne_gui.app import app
from dash import callback_context
from dash.dependencies import Input, Output
from dash import dcc, State, html, ALL, MATCH
from dash.exceptions import PreventUpdate
from evalne_gui.utils import *
from evalne_gui.init_values import *


maximize_opts = [{'label': 'AUROC', 'value': 'auroc'},
                 {'label': 'F-score', 'value': 'f_score'},
                 {'label': 'Precision', 'value': 'precision'},
                 {'label': 'Recall', 'value': 'recall'},
                 {'label': 'Accuracy', 'value': 'accuracy'},
                 {'label': 'Fallout', 'value': 'fallout'},
                 {'label': 'Miss', 'value': 'miss'}]


dashboard_layout = html.Div([

    # --------------------------
    #          Buttons
    # --------------------------
    dbc.Modal(
        id="modal-sm",
        size="sm",
        is_open=False,
        fullscreen=True,
    ),

    html.Br(),
    html.Br(),
    html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Upload(
                        id='upload-conf',
                        children=[
                            html.Button('Import Config', id='imp-conf', className='btn btn-square btn-imp', n_clicks=0),
                        ]
                    )
                ]
            ),
            html.Div(
                children=[
                    html.Button('Export Config', id='exp-conf', className='btn btn-square btn-imp', n_clicks=0),
                ]
            ),
            html.Div(
                children=[
                    html.Button('Clear Config', id='clr-conf', className='btn btn-square btn-imp', n_clicks=0),
                ]
            ),
            html.Div(
                children=[
                    html.Button('Run Evaluation', id='run-eval', className='btn btn-square btn-run', n_clicks=0),
                ]
            ),
        ],
        style={'display': 'flex', 'float': 'right'}
    ),
    dcc.Interval(
        id='btnUpdt-interval',
        interval=1*1000,    # in milliseconds
        n_intervals=0
    ),
    html.Br(),
    html.Br(),

    # --------------------------
    #    Global and sampling
    # --------------------------
    html.H3(children='Global and Node/Edge Sampling Parameters', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(className='plot-area', children=[
    # TASK
    html.Div(
        children=[
            html.Div(
                id='task',
                children=[
                    html.Label(['Evaluation task:']),
                    dcc.Dropdown(
                        id='task-dropdown',
                        options=[{'label': 'Link prediction', 'value': 'lp'},
                                 {'label': 'Sign prediction', 'value': 'sp'},
                                 {'label': 'Network reconstruction', 'value': 'nr'},
                                 {'label': 'Node classification', 'value': 'nc'}],
                        value=init_vals['task-dropdown'],
                        persistence=True,
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'},
            ),
            html.Div(
                id='exprep',
                children=[
                    html.Label(['Experiment repetitions:']),
                    dcc.Input(id="ib-exprep", className='input-box', type="number", value=init_vals['ib-exprep'],
                              min=1, persistence=True)
                ],
                style={'width': '30%', 'padding-right': '5%'},
            ),
            html.Div(
                id='output-fracs',
                children=[
                    html.Div(id='output-box-frace'),
                    dcc.Input(id='ib-frace', type='range', value=init_vals['ib-frace'],
                              min=0, max=0.5, step=0.001, persistence=True)
                ],
                style={'display': 'none'},
            ),
            html.Div(
                id='nc-nodefracs',
                children=[
                    html.Label('Fractions of train nodes (%):'),
                    dcc.Input(id='ib-fracn', className='input-box', type='text',
                              value=init_vals['ib-fracn'], persistence=True)
                ],
                style={'display': 'none'},
            ),
            html.Div(
                id='nc-repperfrac',
                children=[
                    html.Label(['Repetitions per node frac.:']),
                    dcc.Input(id="ib-rpnf", className='input-box', type="number",
                              value=init_vals['ib-rpnf'], min=1, persistence=True)
                ],
                style={'display': 'none'},
            ),
            html.Div(
                id='ee',
                children=[
                    html.Label(['Edge embedding method:']),
                    dcc.Dropdown(
                        id='ee-dropdown',
                        options=[{'label': 'Average', 'value': 'average'},
                                 {'label': 'Hadamard', 'value': 'hadamard'},
                                 {'label': 'Weighted L1', 'value': 'weighted_l1'},
                                 {'label': 'Weighted L2', 'value': 'weighted_l2'}],
                        value=init_vals['ee-dropdown'], multi=True, persistence=True,
                    )
                ],
                style={'width': '30%'},
            ),
        ],
        style={'display': 'flex'}
    ),
    html.Br(),

    # LP_MODEL (dropdown + custom input)
    # EMBED_DIM (text check integer)
    # TIMEOUT (text check integer)
    # SEED (text check integer)
    # VERBOSE (checkbox)?
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Datalist(
                        id='lp-model-opts',
                        children=[
                            html.Option(value="LogisticRegression"),
                            html.Option(value="LogisticRegressionCV"),
                            html.Option(value="sklearn.ensemble.ExtraTreesClassifier()"),
                            html.Option(value="sklearn.svm.LinearSVC()"),
                            html.Option(value="sklearn.svm.LinearSVC(C=1.0, kernel=’rbf’, degree=3)")
                        ]
                    ),
                    html.Label(id='lbl-lpmodel'),
                    dcc.Input(id="ib-lpmodel", className='input-box', type="text",
                              value=init_vals['ib-lpmodel'], list='lp-model-opts', persistence=True)
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Embedding dimension:']),
                    dcc.Input(id="ib-embdim", className='input-box', type="number", value=init_vals['ib-embdim'],
                              min=1, persistence=True),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Evaluation timeout:']),
                    dcc.Input(id="ib-timeout", className='input-box', type="number", value=init_vals['ib-timeout'],
                              min=0, persistence=True),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Random seed:']),
                    dcc.Input(id="ib-seed", className='input-box', type="number", value=init_vals['ib-seed'],
                              min=0, persistence=True),
                ],
                style={'width': '22%'}
            ),
        ],
        style={'display': 'flex'}
    ),
    html.Br(),

    # TRAINTEST_FRAC (text check frac)
    # TRAINVALID_FRAC (text check frac)
    # SPLIT_ALG (dropdown)
    # OWA (dropdown)
    # FE_RATIO (text check integer)
    html.Div(
        id='global-r3-div',
        children=[
            html.Div(
                children=[
                    html.Div(id='ob-trainfrac'),
                    dcc.Input(id='ib-trainfrac', type='range', value=init_vals['ib-trainfrac'],
                              min=0, max=1, step=0.05, persistence=True),
                    html.Br(),
                    html.Div(id='ob-validfrac'),
                    dcc.Input(id='ib-validfrac', type='range', value=init_vals['ib-validfrac'],
                              min=0, max=1, step=0.05, persistence=True),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Split algorithm:']),
                    dcc.Dropdown(
                        id='splitalg-dropdown',
                        options=[{'label': 'Spanning tree', 'value': 'spanning_tree'},
                                 {'label': 'Random', 'value': 'random'},
                                 {'label': 'Naive', 'value': 'naive'},
                                 {'label': 'Fast', 'value': 'fast'},
                                 {'label': 'Timestamp', 'value': 'timestamp'}],
                        value=init_vals['splitalg-dropdown'],
                        persistence=True,
                    ),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Negative sampling:']),
                    dcc.Dropdown(
                        id='negsamp-dropdown',
                        options=[{'label': 'Open world', 'value': 'ow'},
                                 {'label': 'Closed world', 'value': 'cw'}],
                        value=init_vals['negsamp-dropdown'],
                        persistence=True,
                    ),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Datalist(
                id='negsamp-opts',
                children=[
                    html.Option(value="0.5:1"),
                    html.Option(value="1:1"),
                    html.Option(value="2:1"),
                    html.Option(value="4:1"),
                    html.Option(value="10:1")
                ]
            ),
            html.Div(
                children=[
                    html.Label(['Negative edge ratio:']),
                    dcc.Input(id="ib-negratio", className='input-box', type="text", value=init_vals['ib-negratio'],
                              list='negsamp-opts', persistence=True),
                ],
                style={'width': '22%'}
            ),
        ],
    ),
    ]),

    # --------------------------
    # Networks and preprocessing
    # --------------------------
    html.H3(children='Networks and Preprocessing', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(className='plot-area', children=[
    # NAMES (text)
    # INPATHS (text)
    # LABELPATH (text)
    # DIRECTED (radioItems)
    # SEPARATORS (dropdown + custom input)
    # COMMENTS (dropdown + custom input)
    html.Div(
        children=[
            html.Label(['Network names:']),
            dcc.Input(id="ib-nwnames", className='input-box', type="text", value=init_vals['ib-nwnames'],
                      placeholder="Insert network names split by blanks...", persistence=True),
        ],
    ),
    html.Br(),
    html.Div([
        html.Label(['Network edgelist paths:']),
        html.Abbr("\u003f", className='help-qm',
                  title="In order to use relative paths the `evaluation folder` in Settings must be appropriately set.",
                  ),
        dcc.Textarea(
            id='network-paths',
            placeholder='Insert network edgelist paths, one per line...',
            style={
                'width': '100%',
                'height': '100px',
            },
            value=init_vals['network-paths'],
            persistence=True,
        ),
    ]),
    html.Br(),
    html.Div(
        id='network-labelpaths-div',
        children=[
            html.Label(['Network node label paths:']),
            dcc.Textarea(
                id='network-nodelabels',
                placeholder='Insert network node label file paths, one per line...',
                value=init_vals['network-nodelabels'],
                persistence=True,
                style={'width': '100%', 'height': '100px'}
            )
        ],
        style={'display': 'none'}
    ),
    html.Br(),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label(['Network types:']),
                    dcc.RadioItems(
                        id='network-types',
                        options=[
                            {'label': 'Directed', 'value': 'dir'},
                            {'label': 'Undirected', 'value': 'undir'},
                        ],
                        value=init_vals['network-types'],
                        style={'display': 'grid'},
                        persistence=True,
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    html.Label(['Separator per edgelist file:']),
                    dcc.Input(id="ib-separator", className='input-box', type="text", value=init_vals['ib-separator'],
                              placeholder="Insert separators split by blanks...", persistence=True),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    html.Label(['Comment char per edgelist file:']),
                    dcc.Input(id="ib-comment", className='input-box', type="text", value=init_vals['ib-comment'],
                              placeholder="Insert comment chars split by blanks...", persistence=True),
                ],
                style={'width': '30%'}
            ),
        ],
        style={'display': 'flex'}
    ),
    html.Br(),

    # RELABEL (checkbox)
    # DEL_SELFLOOPS (checkbox)
    # SAVE_PREP_NW (checkbox)
    # WRITE_STATS (checkbox)
    # DELIMITER (dropdown + custom input)
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label(['Network preprocessing:']),
                    dcc.Checklist(
                        id='nw-prep-checklist',
                        options=[
                            {'label': 'Relabel nodes (0..N)', 'value': 'rel'},
                            {'label': 'Remove selfloops', 'value': 'selfloops'},
                        ],
                        value=init_vals['nw-prep-checklist'],
                        style={'display': 'grid'},
                        persistence=True,
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    dcc.Checklist(
                        id='nw-prep-checklist2',
                        options=[
                            {'label': 'Save network', 'value': 'save'},
                            {'label': 'Write stats', 'value': 'stats'},
                        ],
                        value=init_vals['nw-prep-checklist2'],
                        style={'display': 'grid'},
                        persistence=True,
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%', 'padding-top': '20px'}
            ),
            html.Div(
                children=[
                    html.Datalist(
                        id='delim-opts',
                        children=[
                            html.Option(value='\\s'),
                            html.Option(value='\\t'),
                            html.Option(value='\\n'),
                            html.Option(value=','),
                            html.Option(value=';'),
                            html.Option(value=':'),
                            html.Option(value='|'),
                        ]
                    ),
                    html.Label(['Preprocessed edgelist delimiter:']),
                    dcc.Input(id="input-prep-delim", className='input-box', type="text",
                              placeholder="Insert or select delimiter...",
                              list='delim-opts', persistence=True),
                ],
                style={'width': '30%'}
            ),
        ],
        style={'display': 'flex'}
    ),
    ]),

    # --------------------------
    #  Heuristics and NE methods
    # --------------------------
    html.H3(children='Heuristics and Embedding Methods', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(className='plot-area', children=[
    # LP_BASELINES
    # NEIGHBOURHOOD
    # METHOD TYPE (library or other)
    # NAMES
    # EMBTYPE
    # WRITE_WEIGHTS
    # WRITE_DIR
    # METHODS
    # TUNE_PARAMS
    # INPUT_DELIM
    # OUTPUT_DELIM
    html.Div(
        id='heuristic-bl-div',
        children=[
            html.Div(
                children=[
                    html.Label(['Heuristic baselines:']),
                    dcc.Checklist(
                        id='baselines-checklist',
                        options=[
                            {'label': 'Common Neighbours', 'value': 'common_neighbours'},
                            {'label': 'Jaccard Coefficient', 'value': 'jaccard_coefficient'},
                            {'label': 'Adamic Adar', 'value': 'adamic_adar_index'},
                            {'label': 'Cosine Similarity', 'value': 'cosine_similarity'},
                            {'label': 'Resource Allocation', 'value': 'resource_allocation_index'},
                            {'label': 'Preferential Attachment', 'value': 'preferential_attachment'},
                        ],
                        value=init_vals['baselines-checklist'],
                        style={'display': 'grid'},
                        persistence=True,
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    dcc.Checklist(
                        id='baselines-checklist2',
                        options=[
                            {'label': 'LHN Index', 'value': 'lhn_index'},
                            {'label': 'Topological Overlap', 'value': 'topological_overlap'},
                            {'label': 'Random Prediction', 'value': 'random_prediction'},
                            {'label': 'Katz exact', 'value': 'katz'},
                            {'label': 'Katz approx', 'value': 'katz'},
                            {'label': 'All Baselines', 'value': 'all_baselines'},
                        ],
                        value=init_vals['baselines-checklist2'],
                        style={'display': 'grid'},
                        persistence=True,
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%', 'padding-top': '20px'}
            ),
            html.Div(
                id='neighbourhood-div',
                children=[
                    html.Label(['Neighbourhood type:']),
                    dcc.Dropdown(
                        id='neighbourhood-dropdown',
                        options=[{'label': 'In neighbourhood', 'value': 'in'},
                                 {'label': 'Out neighbourhood', 'value': 'out'},
                                 {'label': 'In-Out', 'value': 'in out'}],
                        value=init_vals['neighbourhood-dropdown'],
                        persistence=True,
                    ),
                ],
            ),
        ],
    ),
    html.Label(['Embedding methods:']),
    html.Div(id='method', children=[], style={'margin-top': '10px'}),
    html.Div([
        html.Button('+ Add method', id='add-method', className='btn btn-square btn-sm', n_clicks=1),
        html.Button('- Delete method', id='delete-method', className='btn btn-square btn-sm', n_clicks=0),
    ]),
    ]),

    # --------------------------
    #     Metrics and Plots
    # --------------------------
    html.H3(children='Metrics and Plots', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    html.Div(className='plot-area', children=[
    # MAXIMIZE (dropdown)
    # SCORES (dropdown)
    # CURVES (dropdown)
    # PRECATK_VALS (text??)
    html.Div(
        children=[
            html.Div(
                id='maximize-div',
                children=[
                    html.Label(['Metric to maximize:']),
                    dcc.Dropdown(
                        id='maximize-dropdown',
                        value=init_vals['maximize-dropdown'],
                        persistence=True,
                    ),
                ],
            ),
            html.Div(
                id='scores-div',
                children=[
                    html.Label(['Scores to report:']),
                    dcc.Dropdown(
                        id='scores-dropdown',
                        value=init_vals['scores-dropdown'],
                        persistence=True,
                    ),
                ],
            ),
            html.Div(
                id='curves-div',
                children=[
                    html.Label(['Curves to compute:']),
                    dcc.Dropdown(
                        id='curves-dropdown',
                        options=[
                            {'label': 'None', 'value': 'none'},
                            {'label': 'ROC', 'value': 'roc'},
                            {'label': 'PR', 'value': 'pr'},
                            {'label': 'All', 'value': 'all'}],
                        value=init_vals['curves-dropdown'],
                        persistence=True,
                    ),
                ],
            ),
            html.Div(
                id='precatk-div',
                children=[
                    html.Label(['Precision@k values:']),
                    dcc.Input(id="ib-precatk", className='input-box', type="text", value=init_vals['ib-precatk'],
                              placeholder='K values for Prec@k (e.g. 1 10 100 1000)', persistence=True),
                ],
            ),
        ],
        style={'display': 'flex'}
    ),
    html.Br(),
    html.Br(),
    ]),

    # --------------------------
    #       Data storage
    # --------------------------
    dcc.Store(id='conf-values', storage_type='local'),
    dcc.Store(id='method-values', storage_type='local'),
    dcc.Store(id='num-methods', storage_type='local'),
    dcc.Store(id='settings-data', storage_type='local')
])


# --------------------------
#         Callbacks
# --------------------------

@app.callback(Output("global-r3-div", "style"),
              Input("task-dropdown", "value"))
def render_global_section(task):
    """ Renders the global section hiding/showing elements based on the task evaluated. """

    if task == 'nc' or task == 'nr':
        return {'display': 'none'}
    else:
        return {'display': 'flex'}


@app.callback(Output("neighbourhood-div", "style"),
              Input("network-types", "value"))
def toggle_neigh_visibility(val):
    if val == 'dir':
        return {'width': '30%'}
    else:
        return {'display': 'none'}


@app.callback(Output("heuristic-bl-div", "style"),
              Input("task-dropdown", "value"))
def toggle_heuristics_visibility(task):
    if task == 'nc':
        return {'display': 'none'}
    else:
        return {'display': 'flex', 'margin-bottom': '20px'}


@app.callback(Output("modal-sm", "is_open"),
              Output("modal-sm", "children"),
              Input("exp-conf", "n_clicks"),
              Input("clr-conf", "n_clicks"),
              Input("run-eval", "n_clicks"),
              State("modal-sm", "is_open"),
              State('settings-data', 'data'))
def toggle_modal(n1, n2, n3, is_open, settings_data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'exp-conf':
            return not is_open, [dbc.ModalHeader(dbc.ModalTitle("Config exported successfully!"), close_button=False)]
        elif button_id == 'clr-conf':
            return not is_open, [dbc.ModalHeader(dbc.ModalTitle("Config cleared successfully!"), close_button=False)]
        elif button_id == 'run-eval':
            if settings_data is None:
                settings_data = [val for val in init_settings.values()]
            else:
                settings_data = json.loads(settings_data)
            if settings_data[0] == '':
                exec_path = sys.executable
            else:
                exec_path = settings_data[0]
            if evalne_installed(exec_path):
                raise PreventUpdate
            else:
                return not is_open, [dbc.ModalHeader(dbc.ModalTitle("EvalNE is not installed in the current env!"),
                                                     close_button=False)]
        else:
            raise PreventUpdate


@app.callback(Output('run-eval', 'className'),
              Output('run-eval', 'children'),
              Input('btnUpdt-interval', 'n_intervals'))
def set_run_button_state(n_intervals):
    """ Periodic function that checks if an evaluation is running and updates the style of the Start/Stop button. """
    running = get_evalne_proc().running()
    if not running:
        return ['btn btn-square btn-run', 'Start Evaluation']
    else:
        return ['btn btn-square btn-run btn-active', 'Stop Evaluation']


@app.callback(Output('run-eval', 'n_clicks'),
              Input('run-eval', 'n_clicks'),
              State('conf-values', 'data'),
              State('method-values', 'data'),
              State('settings-data', 'data'))
def start_stop_eval(n_clicks, conf_vals, methods_vals, settings_data):
    """ Function that starts/stops an evaluation when the Start/Stop button is pressed. """
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        if int(n_clicks) % 2 == 0:
            # Even clicks stop eval and set button text to `Run Evaluation`
            get_evalne_proc().stop()
            return n_clicks
        else:
            # Odd clicks start eval and set button to `Stop Evaluation`
            if settings_data is None:
                settings_data = [val for val in init_settings.values()]
            else:
                settings_data = json.loads(settings_data)
            if settings_data[0] == '':
                exec_path = sys.executable
            else:
                exec_path = settings_data[0]
            if settings_data[1] == '':
                eval_path = os.getcwd()
            else:
                eval_path = settings_data[1]
            ini_path = os.path.join(eval_path, 'conf_gui_{}.ini'.format(datetime.datetime.now().strftime("%m%d_%H%M")))
            console_out = os.path.join(eval_path, 'console.out')

            # Load config data
            conf_vals = json.loads(conf_vals)
            conf_dict = dict(zip(init_vals.keys(), conf_vals))
            methods_vals = json.loads(methods_vals)
            methods_dict = dict(zip(method_init_vals.keys(), methods_vals))

            # Export conf.ini and run evaluation
            export_config_file(ini_path, conf_dict, methods_dict)
            proc = get_evalne_proc()
            proc.start('{} -m evalne {}'.format(exec_path, ini_path), console_out, eval_path, True)

            return n_clicks


@app.callback(Output('exp-conf', 'n_clicks'),
              Input('exp-conf', 'n_clicks'),
              State('conf-values', 'data'),
              State('method-values', 'data'),
              State('settings-data', 'data'))
def export_config(n_clicks, conf_vals, methods_vals, settings_data):
    """ This function is executed when the user preses the export config button. """
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        if settings_data is None:
            settings_data = [val for val in init_settings.values()]
        else:
            settings_data = json.loads(settings_data)
        if settings_data[1] == '':
            eval_path = os.getcwd()
        else:
            eval_path = settings_data[1]
        conf_vals = json.loads(conf_vals)
        methods_vals = json.loads(methods_vals)
        conf_path = 'conf_gui_{}.ini'.format(datetime.datetime.now().strftime("%m%d_%H%M"))
        conf_dict = dict(zip(init_vals.keys(), conf_vals))
        methods_dict = dict(zip(method_init_vals.keys(), methods_vals))
        export_config_file(os.path.join(eval_path, conf_path), conf_dict, methods_dict)
        return n_clicks


@app.callback(Output('ob-trainfrac', 'children'),
              Input('ib-trainfrac', 'value'))
def render_train_perc(frac):
    """ Function that updates the train frac percentage when the slider moves. """
    val = int(float(frac) * 100)
    return 'Train-test fraction ({}%):'.format(val)


@app.callback(Output('ob-validfrac', 'children'),
              Input('ib-validfrac', 'value'))
def render_valid_perc(frac):
    """ Function that updates the valid frac percentage when the slider moves. """
    val = int(float(frac) * 100)
    return 'Train-valid. fraction ({}%):'.format(val)


@app.callback(Output('output-box-frace', 'children'),
              Input('ib-frace', 'value'))
def render_nodepairs_perc(frac):
    """ Function that updates the node-pair frac when the slider moves. """
    val = float(frac) * 100
    return 'Node pairs to evaluate ({:4.1f}%):'.format(val)


@app.callback([Output('task', 'style'),
               Output('exprep', 'style'),
               Output('output-fracs', 'style'),
               Output('nc-nodefracs', 'style'),
               Output('nc-repperfrac', 'style'),
               Output('ee', 'style'),
               Output('lbl-lpmodel', 'children'),
               Output('network-labelpaths-div', 'style'),
               Output('maximize-dropdown', 'options'),
               Output('scores-dropdown', 'options')],
               Input('task-dropdown', 'value'))
def render_content(task):
    """ Function that updates the Dashboard elements and style based on the task to be evaluated. """
    if task == 'lp' or task == 'sp':
        return [{'width': '30%', 'padding-right': '5%'},                        # task
                {'width': '30%', 'padding-right': '5%'},                        # exprep
                {'display': 'none'},                                            # nr fracs
                {'display': 'none'},                                            # nc nodefracs
                {'display': 'none'},                                            # nc repperfrac
                {'width': '30%'},                                               # ee method
                'Binary classifier:',
                {'display': 'none'},
                maximize_opts,
                maximize_opts + [{'label': 'All', 'value': 'all'}]]
    elif task == 'nr':
        return [{'width': '30%', 'padding-right': '5%'},                        # task
                {'display': 'none'},                                            # exprep
                {'width': '30%', 'padding-right': '5%'},                        # nr fracs
                {'display': 'none'},                                            # nc nodefracs
                {'display': 'none'},                                            # nc repperfrac
                {'width': '30%'},                                               # ee method
                'Binary classifier:',
                {'display': 'none'},
                maximize_opts,
                maximize_opts + [{'label': 'All', 'value': 'all'}]]
    elif task == 'nc':
        return [{'width': '30%', 'padding-right': '5%'},                        # task
                {'display': 'none'},                                            # exprep
                {'display': 'none'},                                            # nr fracs
                {'width': '30%', 'padding-right': '5%'},                        # nc nodefracs
                {'width': '30%'},                                               # nc repperfrac
                {'display': 'none'},                                            # ee method
                'Multi-label classifier:',
                {'display': 'block'},
                [{'label': 'F1-micro', 'value': 'f1_micro'},
                 {'label': 'F1-macro', 'value': 'f1_macro'},
                 {'label': 'F1-weighted', 'value': 'f1_weighted'}],
                [{'label': 'All', 'value': 'all'},
                 {'label': 'F1-micro', 'value': 'f1_micro'},
                 {'label': 'F1-macro', 'value': 'f1_macro'},
                 {'label': 'F1-weighted', 'value': 'f1_weighted'}]]


@app.callback([[Output(key, 'value') for key in init_vals.keys()]],
              Output('conf-values', 'data'),
              [[Input(key, 'value') for key in init_vals.keys()]],
              Input('clr-conf', 'n_clicks'),
              Input('upload-conf', 'contents'),
              State('conf-values', 'data'))
def refresh_config(data, nclick, upload, old_data):
    """ This function stores and loads data from a dcc.Store on page-refresh/tab-change/user-action. """
    ctx = callback_context
    if not ctx.triggered:
        if old_data is None:
            # Triggered on first ui load
            res = [val for val in init_vals.values()]
            return res, json.dumps(res)
        else:
            # Triggered when changing tabs/restarting
            od = json.loads(old_data)
            return od, old_data
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'clr-conf':
            # Triggered by user click
            res = [val for val in init_vals.values()]
            return res, json.dumps(res)
        elif button_id == 'upload-conf':
            conf_vals = get_config_vals(upload)
            return conf_vals, json.dumps(conf_vals)
        else:
            # Triggered when any value is changed in conf
            if button_id == 'task-dropdown':
                if data[0] == 'nc':
                    data[27] = 'f1_micro'
                else:
                    data[27] = 'auroc'
            return data, json.dumps(data)


@app.callback(Output('method', 'children'),
              Output('num-methods', 'data'),
              Input('add-method', 'n_clicks'),
              Input('delete-method', 'n_clicks'),
              Input('clr-conf', 'n_clicks'),
              Input('upload-conf', 'contents'),
              State('method', 'children'),
              State('num-methods', 'data'),)
def show_methods(add_nclk, del_nclk, clr_nclk, upload, curr_children, num_methods):
    """ This function manages the number of methods visible at any time based on add/del clicks. """
    # Get callback context to detect which button triggered it
    ctx = callback_context
    if not ctx.triggered:
        if curr_children is None:
            # Triggered when UI is initialized
            return append_children_divs(1)
        else:
            # Triggered on page refresh/states change
            num_methods = json.loads(num_methods) if num_methods is not None else 1
            return append_children_divs(num_methods)

    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'add-method':
            # Add new method div
            el = get_method_div(len(curr_children) + 1)
            curr_children.append(el)
            return curr_children, json.dumps(len(curr_children))
        elif button_id == 'delete-method':
            # Remove last method div
            if len(curr_children) == 0:
                return curr_children, json.dumps(0)
            curr_children.pop()
            return curr_children, json.dumps(len(curr_children))
        elif button_id == 'clr-conf':
            # Reset to one method div
            return append_children_divs(1)
        elif button_id == 'upload-conf':
            return append_children_divs(get_num_methods(upload))
        else:
            raise PreventUpdate


@app.callback([[Output({'type': key, 'index': ALL}, 'value') for key in method_init_vals.keys()]],
              Output('method-values', 'data'),
              [[Input({'type': key, 'index': ALL}, 'value') for key in method_init_vals.keys()]],
              Input('num-methods', 'data'),
              Input('clr-conf', 'n_clicks'),
              Input('upload-conf', 'contents'),
              State('method-values', 'data'))
def save_method_values(values, num_methods, nclicks, upload, old_data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'num-methods':
            # Triggered when a method in added or removed
            res = json.loads(old_data)
            num_methods = json.loads(num_methods)
            if len(res[0]) < num_methods:
                # Method added
                init_values = [val for val in method_init_vals.values()]
                for ind, val in enumerate(res):
                    val.append(init_values[ind])
            elif len(res[0]) > num_methods:
                # Method removed
                for val in res:
                    val.pop()
            else:
                raise PreventUpdate
        elif button_id == 'clr-conf':
            # Triggered when used presses clear conf button
            res = [[val] for val in method_init_vals.values()]
        elif button_id == 'upload-conf':
            res = get_config_methods(upload)
        else:
            if values[0][0] is None:
                # Triggered when page refreshed or ui init
                if len(values[0]) > 1:
                    # Page refresh
                    res = json.loads(old_data)
                else:
                    # UI init
                    if old_data is not None:
                        res = json.loads(old_data)
                    else:
                        res = [[val] for val in method_init_vals.values()]
            else:
                # Triggered when method values are modified
                res = values

    return res, json.dumps(res)


@app.callback([Output({'type': 'emb-type-div', 'index': MATCH}, 'style'),
               Output({'type': 'm-opts-div', 'index': MATCH}, 'style'),
               Output({'type': 'm-tune-div', 'index': MATCH}, 'style'),
               Output({'type': 'm-input-delim-div', 'index': MATCH}, 'style'),
               Output({'type': 'm-output-delim-div', 'index': MATCH}, 'style')],
              Input({'type': 'm-lib-dropdown', 'index': MATCH}, 'value'))
def toggle_method_style(m_type):
    if m_type:
        if m_type == 'opne':
            return [{'display': 'none'},
                    {'display': 'none'},
                    {'width': '100%'},
                    {'display': 'none'},
                    {'display': 'none'}]
        else:
            return [{'width': '22%', 'padding-right': '4%'},
                    {'width': '22%'},
                    {'width': '48%', 'padding-right': '4%'},
                    {'width': '22%', 'padding-right': '4%'},
                    {'width': '22%'}]
    else:
        raise PreventUpdate


@app.callback(Output("maximize-div", "style"),
              Output("scores-div", "style"),
              Output("curves-div", "style"),
              Output("precatk-div", "style"),
              Input("task-dropdown", "value"))
def render_metrics_section(task):
    """ Renders the metrics section based on the task evaluated. """

    if task == 'nc':
        return [{'width': '48%', 'padding-right': '4%'},
                {'width': '48%'},
                {'display': 'none'},
                {'display': 'none'}]
    else:
        return [{'width': '22%', 'padding-right': '4%'},
                {'width': '22%', 'padding-right': '4%'},
                {'width': '22%', 'padding-right': '4%'},
                {'width': '22%'}]


# --------------------------
#      Other Functions
# --------------------------

def append_children_divs(val):
    children = []
    for i in range(val):
        el = get_method_div(i + 1)
        children.append(el)
    return children, json.dumps(val)


def get_method_div(val):
    el = html.Div(
        children=[
            html.Div(children=[html.Label(['NE method {}:'.format(val)])],
                     style={'display': 'list-item', 'margin-left': '25px'}),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Label(['Method type:']),
                                    dcc.Dropdown(
                                        id={
                                            'index': val,
                                            'type': 'm-lib-dropdown'
                                        },
                                        options=[
                                            {'label': 'OpenNE', 'value': 'opne'},
                                            {'label': 'GEM', 'value': 'gem'},
                                            {'label': 'KarateClub', 'value': 'kk'},
                                            {'label': 'Other', 'value': 'other'}],
                                        persistence=False,
                                    ),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                children=[
                                    html.Label(['Method name:']),
                                    dcc.Input(
                                        id={
                                            'index': val,
                                            'type': 'm-name'
                                        }, className='input-box', type='text',
                                        placeholder="Insert method name...", persistence=False, debounce=True),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                id={
                                    'index': val,
                                    'type': 'emb-type-div'
                                },
                                children=[
                                    html.Label(['Embedding type:']),
                                    dcc.Dropdown(
                                        id={
                                            'index': val,
                                            'type': 'm-type-dropdown'
                                        },
                                        options=[{'label': 'Node embedding', 'value': 'ne'},
                                                 {'label': 'Edge embedding', 'value': 'ee'},
                                                 {'label': 'End to end', 'value': 'e2e'}],
                                        persistence=False,
                                    ),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                id={
                                    'index': val,
                                    'type': 'm-opts-div'
                                },
                                children=[
                                    html.Label(['Method input edgelist:']),
                                    dcc.Checklist(
                                        id={
                                            'index': val,
                                            'type': 'm-opts'
                                        },
                                        options=[
                                            {'label': 'Write weights', 'value': 'weights'},
                                            {'label': 'Write both dir', 'value': 'dir'},
                                        ],
                                        style={'display': 'grid'},
                                        persistence=False,
                                    ),
                                ],
                                style={'width': '22%'}
                            ),
                        ],
                        style={'display': 'flex'}
                    ),
                    html.Br(),
                    html.Div(
                        children=[
                            html.Label(['Method command line call:']),
                            html.Abbr("\u003f", className='help-qm',
                                      title="In order to use relative paths the `evaluation folder` "
                                            "in Settings must be appropriately set.",
                                      ),
                            dcc.Input(
                                id={
                                    'index': val,
                                    'type': 'm-cmd'
                                }, className='input-box', type="text",
                                placeholder=
                                "Insert cmd call (e.g. ./venv/bin/python main.py --input {} --output {} --dim {})",
                                persistence=False, debounce=True),
                        ],
                    ),
                    html.Br(),
                    html.Div(
                        children=[
                            html.Div(
                                id={
                                    'index': val,
                                    'type': 'm-tune-div'
                                },
                                children=[
                                    html.Label(['Tune hyper-parameters:']),
                                    dcc.Input(
                                        id={
                                            'index': val,
                                            'type': 'm-tune'
                                        }, className='input-box', type="text",
                                        placeholder="Insert hyper-parameters to tune (e.g. --p 0.5 1 --q 1 2)",
                                        persistence=False, debounce=True),
                                ],
                                style={'width': '48%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                id={
                                    'index': val,
                                    'type': 'm-input-delim-div'
                                },
                                children=[
                                    html.Label(['Input delimiter:']),
                                    dcc.Input(
                                        id={
                                            'index': val,
                                            'type': 'm-input-delim'
                                        }, className='input-box', type="text",
                                        placeholder="Insert or select delimiter...",
                                        list='delim-opts', persistence=False, debounce=True),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                id={
                                    'index': val,
                                    'type': 'm-output-delim-div'
                                },
                                children=[
                                    html.Label(['Output delimiter:']),
                                    dcc.Input(
                                        id={
                                            'index': val,
                                            'type': 'm-output-delim'
                                        }, className='input-box', type="text",
                                        placeholder="Insert or select delimiter...",
                                        list='delim-opts', persistence=False, debounce=True),
                                ],
                                style={'width': '22%'}
                            ),
                        ],
                        style={'display': 'flex'}
                    ),
                ],
                style={'margin-left': '30px', 'margin-top': '10px', 'margin-bottom': '10px'}
            ),
            html.Br(),
        ]
    )
    return el
