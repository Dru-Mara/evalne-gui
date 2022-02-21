import json
import sys
import dash

from app import app
from dash import callback_context
from dash.dependencies import Input, Output
from dash import dcc, State, html, ALL, MATCH
from dash.exceptions import PreventUpdate
from utils import *
from collections import OrderedDict

# TODO: How to persist/reset the method divs?
# TODO: Make export conf actually export the data to a conf.ini file
# TODO: Make run actually evaluate using conf file.
# TODO: Make import work.

max_methods = 5

init_vals = OrderedDict({'task-dropdown': 'LP',
                         'ee-dropdown': 'Avg',
                         'ib-exprep': 5,
                         'ib-frace': 0.001,
                         'ib-rpnf': 5,
                         'ib-fracn': '10, 50, 90',
                         'ib-lpmodel': 'LogisticRegressionCV',
                         'ib-embdim': 128,
                         'ib-timeout': 0,
                         'ib-seed': 42,
                         'ib-trainfrac': 0.8,
                         'ib-validfrac': 0.9,
                         'splitalg-dropdown': 'st',
                         'negsamp-dropdown': 'ow',
                         'ib-negratio': '1:1',
                         'ib-nwnames': '',
                         'network-paths': '',
                         'network-nodelabels': '',
                         'network-types': 'undir',
                         'ib-separator': '',
                         'ib-comment': '',
                         'nw-prep-checklist': ['rel', 'selfloops'],
                         'nw-prep-checklist2': [],
                         'input-prep-delim': 'Comma',
                         'baselines-checklist': [],
                         'baselines-checklist2': [],
                         'neighbourhood-dropdown': 'inout',
                         'maximize-dropdown': 'auc',
                         'scores-dropdown': 'all',
                         'curves-dropdown': 'roc',
                         'ib-precatk': ''})


maximize_opts = [{'label': 'AUC', 'value': 'auc'},
                 {'label': 'F-score', 'value': 'fscore'},
                 {'label': 'Precision', 'value': 'prec'},
                 {'label': 'Recall', 'value': 'rec'},
                 {'label': 'Accuracy', 'value': 'acc'},
                 {'label': 'Fallout', 'value': 'fall'},
                 {'label': 'Miss', 'value': 'miss'}]


dashboard_layout = html.Div([

    html.Br(),
    html.Br(),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Button('Import Config', id='imp-conf', className='btn btn-square btn-imp', n_clicks=0),
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
    html.H3(children='Global and Edge Sampling Parameters', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    # TASK
    html.Div(
        children=[
            html.Div(
                id='task',
                children=[
                    html.Label(['Evaluation task:']),
                    dcc.Dropdown(
                        id='task-dropdown',
                        options=[{'label': 'Link prediction', 'value': 'LP'},
                                 {'label': 'Sign prediction', 'value': 'SP'},
                                 {'label': 'Network reconstruction', 'value': 'NR'},
                                 {'label': 'Node classification', 'value': 'NC'}],
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
                              min=0, persistence=True)
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
                              value=init_vals['ib-rpnf'], min=0, persistence=True)
                ],
                style={'display': 'none'},
            ),
            html.Div(
                id='ee',
                children=[
                    html.Label(['Edge embedding method:']),
                    dcc.Dropdown(
                        id='ee-dropdown',
                        options=[{'label': 'Average', 'value': 'Avg'},
                                 {'label': 'Hadamard', 'value': 'Had'},
                                 {'label': 'Weighted L1', 'value': 'WL1'},
                                 {'label': 'Weighted L2', 'value': 'WL2'}],
                        value=init_vals['ee-dropdown'],
                        persistence=True,
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
    # VERBOSE (checkbox)
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
                    html.Label(['Link prediction model:']),
                    dcc.Input(id="ib-lpmodel", className='input-box', type="text",
                              value=init_vals['ib-lpmodel'], list='lp-model-opts', persistence=True)
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Embedding dimensionality:']),
                    dcc.Input(id="ib-embdim", className='input-box', type="number", value=init_vals['ib-embdim'],
                              min=0, persistence=True),
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
                        options=[{'label': 'Spanning tree', 'value': 'st'},
                                 {'label': 'Random', 'value': 'rand'},
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
                    html.Option(value="1:1"),
                    html.Option(value="1:2"),
                    html.Option(value="2:1"),
                    html.Option(value="1:10"),
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
        style={'display': 'flex'}
    ),

    # --------------------------
    # Networks and preprocessing
    # --------------------------
    html.H3(children='Networks and Preprocessing', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

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
                      placeholder="Insert network names separated with blanks...", persistence=True),
        ],
    ),
    html.Br(),
    html.Div([
        html.Label(['Network edgelist paths:']),
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
                              placeholder="Insert separators with banks...", persistence=True),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    html.Label(['Comment char per edgelist file:']),
                    dcc.Input(id="ib-comment", className='input-box', type="text", value=init_vals['ib-comment'],
                              placeholder="Insert comment chars with banks...", persistence=True),
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
                            html.Option(value='Blank'),
                            html.Option(value='Tab'),
                            html.Option(value='Comma'),
                            html.Option(value='Semicolon'),
                            html.Option(value='Bar')
                        ]
                    ),
                    html.Label(['Preprocessed edgelist delimiter:']),
                    dcc.Input(id="input-prep-delim", className='input-box', type="text",
                              value=init_vals['input-prep-delim'], list='delim-opts', persistence=True),
                ],
                style={'width': '30%'}
            ),
        ],
        style={'display': 'flex'}
    ),

    # --------------------------
    #  Baselines and NE methods
    # --------------------------
    html.H3(children='Baselines and NE Methods', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),
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
        children=[
            html.Div(
                children=[
                    html.Label(['Baseline methods:']),
                    dcc.Checklist(
                        id='baselines-checklist',
                        options=[
                            {'label': 'Common Neighbours', 'value': 'cn'},
                            {'label': 'Jaccard Coefficient', 'value': 'jc'},
                            {'label': 'Adamic Adar', 'value': 'aa'},
                            {'label': 'Cosine Similarity', 'value': 'cs'},
                            {'label': 'Resource Allocation', 'value': 'ra'},
                            {'label': 'Preferential Attachment', 'value': 'pa'},
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
                            {'label': 'LHN Index', 'value': 'lhn'},
                            {'label': 'Topological Overlap', 'value': 'to'},
                            {'label': 'Random Prediction', 'value': 'rand'},
                            {'label': 'Katz exact', 'value': 'katz'},
                            {'label': 'Katz approx', 'value': 'katza'},
                            {'label': 'All Baselines', 'value': 'bl'},
                        ],
                        value=init_vals['baselines-checklist2'],
                        style={'display': 'grid'},
                        persistence=True,
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%', 'padding-top': '20px'}
            ),
            html.Div(
                children=[
                    html.Label(['Neighbourhood type:']),
                    dcc.Dropdown(
                        id='neighbourhood-dropdown',
                        options=[{'label': 'In neighbourhood', 'value': 'in'},
                                 {'label': 'Out neighbourhood', 'value': 'out'},
                                 {'label': 'In-Out', 'value': 'inout'}],
                        value=init_vals['neighbourhood-dropdown'],
                        persistence=True,
                    ),
                ],
                style={'width': '30%'}
            ),
        ],
        style={'display': 'flex'}
    ),
    html.Br(),
    html.Div(id='method', children=[]),
    html.Div([
        html.Button('+ Add method', id='add-method', className='btn btn-square btn-sm', n_clicks=1),
        html.Button('- Delete method', id='delete-method', className='btn btn-square btn-sm', n_clicks=0),
    ]),

    # --------------------------
    #     Metrics and Plots
    # --------------------------
    html.H3(children='Metrics and Plots', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),
    # MAXIMIZE (dropdown)
    # SCORES (dropdown)
    # CURVES (dropdown)
    # PRECATK_VALS (text??)
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label(['Metric to maximize:']),
                    dcc.Dropdown(
                        id='maximize-dropdown',
                        value=init_vals['maximize-dropdown'],
                        persistence=True,
                    ),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Scores to report:']),
                    dcc.Dropdown(
                        id='scores-dropdown',
                        value=init_vals['scores-dropdown'],
                        persistence=True,
                    ),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
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
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Precision@k values:']),
                    dcc.Input(id="ib-precatk", className='input-box', type="text", value=init_vals['ib-precatk'],
                              placeholder='K values for Prec@k (e.g. 1 10 100 1000)', persistence=True),
                ],
                style={'width': '22%'}
            ),
        ],
        style={'display': 'flex'}
    ),
    html.Br(),
    html.Br(),
    dcc.Store(id='conf-values', storage_type='local'),
    dcc.Store(id='method-values', storage_type='local'),
    dcc.Store(id='num-methods', storage_type='local')
])


# Callbacks
@app.callback(Output({'type': 'lib-dropdown', 'index': ALL}, 'value'),
              Output('method-values', 'data'),
              Input({'type': 'lib-dropdown', 'index': ALL}, 'value'),
              Input('clr-conf', 'n_clicks'),
              State({'type': 'lib-dropdown', 'index': ALL}, 'id'),
              State('method-values', 'data'),
              State('num-methods', 'data'))
def save_methods(lib_ddvalues, nclick, ids, old_data, num_methods):
    ctx = callback_context
    print('call')
    num_methods = int(num_methods)
    #print(lib_ddvalues)
    #print(ids)
    #print(old_data)
    #return 'other', json.loads({})
    if not ctx.triggered:
        if old_data is None:
            print('init')
            # Triggered on first ui load
            res = ['other']
            print(res)
            return res, json.dumps(res)
        else:
            # Triggered when changing tabs/restarting
            print('loading json')
            #print(old_data)
            #print(num_methods)
            od = json.loads(old_data)
            #print(od)
            if len(od) == num_methods:
                print('equal')
                res = list(od)
            elif len(od) < num_methods:
                print('larger')
                res = od + ['other']
            else:
                print('smaller')
                res = od[:num_methods]
            print(res)
            return res, json.dumps(res)

    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'clr-conf':
            # Triggered by user click
            res = ['other'] * num_methods
            print('clear')
            print(res)
            return res, json.dumps(res)
        else:
            # Triggered when any value is changed in conf
            if all(v is None for v in lib_ddvalues):
                print('all are none')
                res = json.loads(old_data)
            else:
                res = lib_ddvalues
            print('dump values')
            #print(lib_ddvalues)
            #print(old_data)
            print(res)
            return res, json.dumps(res)


# @app.callback([[Output('lib-dropdown-{}'.format(val+1), 'value') for val in range(max_methods)]],
#               Output('method-values', 'data'),
#               [[Input('lib-dropdown-{}'.format(val+1), 'value') for val in range(max_methods)]],
#               Input('clr-conf', 'n_clicks'),
#               State('method-values', 'data'))
# def save_methods(sa_list, nclick, old_data):
#     ctx = callback_context
#
#     if not ctx.triggered:
#         if old_data is None:
#             print('init')
#             # Triggered on first ui load
#             res = ['other'] * max_methods
#             return res, json.dumps(res)
#         else:
#             # Triggered when changing tabs/restarting
#             print('loading json')
#             od = json.loads(old_data)
#             return od, old_data
#     else:
#         button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#         if button_id == 'clr-conf':
#             # Triggered by user click
#             print('clear')
#             res = ['other'] * max_methods
#             return res, json.dumps(res)
#         else:
#             # Triggered when any value is changed in conf
#             print('dump values')
#             return sa_list, json.dumps(sa_list)


@app.callback([[Output(key, 'value') for key in init_vals.keys()]],
              Output('conf-values', 'data'),
              [[Input(key, 'value') for key in init_vals.keys()]],
              Input('clr-conf', 'n_clicks'),
              State('conf-values', 'data'))
def clear_config(data, nclick, old_data):
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
        else:
            # Triggered when any value is changed in conf
            if button_id == 'task-dropdown':
                if data[0] == 'NC':
                    data[27] = 'f1_micro'
                else:
                    data[27] = 'auc'
            return data, json.dumps(data)


@app.callback(Output('run-eval', 'className'),
              Output('run-eval', 'children'),
              Input('btnUpdt-interval', 'n_intervals'))
def set_run_button_state(n_intervals):
    """ Periodic function that checks if an evaluation is running and updates the style of the Start/Stop button. """
    proc = search_process('evalne')
    if proc is None:
        return ['btn btn-square btn-run', 'Start Evaluation']
    else:
        return ['btn btn-square btn-run btn-active', 'Stop Evaluation']


@app.callback(Output('run-eval', 'n_clicks'),
              Input('run-eval', 'n_clicks'))
def set_active(n_clicks):
    """ Function that starts/stops an evaluation when the Start/Stop button is pressed. """
    ctx = callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        if int(n_clicks) % 2 == 0:
            # Even clicks stop eval and set button text to `Run Evaluation`
            stop_process('evalne')
            return n_clicks
        else:
            # Odd clicks start eval and set button to `Stop Evaluation`
            exec_path = sys.executable
            conf_path = '/home/almara/Desktop/EvalNE/examples/dummy_conf.ini'
            start_process('{} -m evalne {}'.format(exec_path, conf_path), True)
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
               Output('network-labelpaths-div', 'style'),
               Output('maximize-dropdown', 'options'),
               Output('scores-dropdown', 'options')],
               Input('task-dropdown', 'value'))
def render_content(task):
    """ Function that updates the Dashboard elements and style based on the task to be evaluated. """
    if task == 'LP' or task == 'SP':
        return [{'width': '30%', 'padding-right': '5%'},                        # task
                {'width': '30%', 'padding-right': '5%'},                        # exprep
                {'display': 'none'},                                            # nr fracs
                {'display': 'none'},                                            # nc nodefracs
                {'display': 'none'},                                            # nc repperfrac
                {'width': '30%'},                                               # ee method
                {'display': 'none'},
                maximize_opts,
                maximize_opts + [{'label': 'All', 'value': 'all'}]]
    elif task == 'NR':
        return [{'width': '30%', 'padding-right': '5%'},                        # task
                {'display': 'none'},                                            # exprep
                {'width': '30%', 'padding-right': '5%'},                        # nr fracs
                {'display': 'none'},                                            # nc nodefracs
                {'display': 'none'},                                            # nc repperfrac
                {'width': '30%'},                                               # ee method
                {'display': 'none'},
                maximize_opts,
                maximize_opts + [{'label': 'All', 'value': 'all'}]]
    elif task == 'NC':
        return [{'width': '22%', 'padding-right': '4%'},                        # task
                {'display': 'none'},                                            # exprep
                {'display': 'none'},                                            # nr fracs
                {'width': '22%', 'padding-right': '4%'},                        # nc nodefracs
                {'width': '22%', 'padding-right': '4%'},                        # nc repperfrac
                {'width': '22%'},                                               # ee method
                {'display': 'block'},
                [{'label': 'F1-micro', 'value': 'f1_micro'},
                 {'label': 'F1-macro', 'value': 'f1_macro'},
                 {'label': 'F1-weighted', 'value': 'f1_weighted'}],
                [{'label': 'All', 'value': 'all'},
                 {'label': 'F1-micro', 'value': 'f1_micro'},
                 {'label': 'F1-macro', 'value': 'f1_macro'},
                 {'label': 'F1-weighted', 'value': 'f1_weighted'}]]


@app.callback(Output('method', 'children'),
              Output('add-method', 'n_clicks'),
              Output('num-methods', 'data'),
              Input('add-method', 'n_clicks'),
              Input('delete-method', 'n_clicks'),
              State('method', 'children'),
              State('add-method', 'n_clicks'),
              State('num-methods', 'data'))
def add_method(val, delete, children, n_clicks, old_data):
    """ This function manages the number of methods visible at any time based on add/del clicks. """
    # Get callback context to detect which button triggered it
    ctx = callback_context
    if not ctx.triggered:
        if old_data is None:
            # add_method n_clicks always starts at 1 to display the first method
            if val:
                el = get_method_div(val)
                children.append(el)
                return children, val, json.dumps(val)
            else:
                raise PreventUpdate
        else:
            loaded_val = json.loads(old_data)
            # Since add_method n_clicks counts from 1 we do i+1 for the range
            children = []
            for i in range(loaded_val):
                el = get_method_div(i+1)
                children.append(el)
            print('refresh')
            return children, loaded_val, old_data
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'add-method':
            children = []
            for i in range(val):
                el = get_method_div(i+1)
                children.append(el)
            print('add')
            return children, val, json.dumps(val)

        elif button_id == 'delete-method':
            children = []
            for i in range(n_clicks-1):
                el = get_method_div(i + 1)
                children.append(el)
            print('delete')
            return children, n_clicks - 1, json.dumps(n_clicks - 1)

        else:
            raise PreventUpdate


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
                                            'type': 'lib-dropdown'
                                        }, #'lib-dropdown-{}'.format(val),
                                        options=[
                                            {'label': 'OpenNE', 'value': 'opne'},
                                            {'label': 'GEM', 'value': 'gem'},
                                            {'label': 'KarateClub', 'value': 'kk'},
                                            {'label': 'Other', 'value': 'other'}],
                                        #value='other',
                                        persistence=True,
                                    ),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                children=[
                                    html.Label(['Method name:']),
                                    dcc.Input(id='name-m-{}'.format(val), className='input-box', type='text',
                                              placeholder="Insert method name...", persistence=True),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                children=[
                                    html.Label(['Embedding type:']),
                                    dcc.Dropdown(
                                        id='mtype-dropdown-{}'.format(val),
                                        options=[{'label': 'Node embedding', 'value': 'ne'},
                                                 {'label': 'Edge embedding', 'value': 'ee'},
                                                 {'label': 'End to end', 'value': 'e2e'}],
                                        value='ne',
                                        persistence=True,
                                    ),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                children=[
                                    html.Label(['Method input edgelist:']),
                                    dcc.Checklist(
                                        id='opts-{}'.format(val),
                                        options=[
                                            {'label': 'Write weights', 'value': 'weights'},
                                            {'label': 'Write both dir', 'value': 'dir'},
                                        ],
                                        value=['dir'],
                                        style={'display': 'grid'},
                                        persistence=True,
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
                            dcc.Input(id='cmd-m-{}'.format(val), className='input-box', type="text",
                                      placeholder="Insert cmd call (e.g. ./venv/bin/python main.py --input {} --output {} --dim {})",
                                      persistence=True),
                        ],
                    ),
                    html.Br(),
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Label(['Tune hyperparameters:']),
                                    dcc.Input(id='tune-m-{}'.format(val), className='input-box', type="text",
                                              placeholder="Insert hyperparameters to tune (e.g. --p 0.5 1 --q 1 2)",
                                              persistence=True),
                                ],
                                style={'width': '48%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                children=[
                                    html.Label(['Input delimiter:']),
                                    dcc.Input(id='input-method-delim-{}'.format(val), className='input-box',
                                              type="text", value='Comma', list='delim-opts', persistence=True),
                                ],
                                style={'width': '22%', 'padding-right': '4%'}
                            ),
                            html.Div(
                                children=[
                                    html.Label(['Output delimiter:']),
                                    dcc.Input(id='output-method-delim-{}'.format(val), className='input-box',
                                              type="text", value='Comma', list='delim-opts', persistence=True),
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
