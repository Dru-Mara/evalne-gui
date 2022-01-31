
from app import app
from dash import callback_context
from dash.dependencies import Input, Output
from dash import dcc, State, html
from dash.exceptions import PreventUpdate


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
                    html.Button('Run Evaluation', id='run-eval', className='btn btn-square btn-run', n_clicks=0),
                ]
            ),
        ],
        style={'display': 'flex', 'float': 'right'}
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
                        value='LP',
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(id='exprep'),
            html.Div(id='output-fracs'),
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
                       value='Avg',
                    )
                ],
                style={'width': '30%'}
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
                    dcc.Input(id="input-lp-model", className='input-box', type="text", value='LogisticRegressionCV',
                              list='lp-model-opts')
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Embedding dimensionality:']),
                    dcc.Input(id="input-box-2", className='input-box', type="number", value=128, min=0),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Evaluation timeout:']),
                    dcc.Input(id="input-box-3", className='input-box', type="number", value=0, min=0),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Random seed:']),
                    dcc.Input(id="input-box-4", className='input-box', type="number", value=42, min=0),
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
                    html.Div(id='output-box-5'),
                    dcc.Input(id='input-box-5', type='range', value=0.8, min=0, max=1, step=0.05),
                    html.Br(),
                    html.Div(id='output-box-6'),
                    dcc.Input(id='input-box-6', type='range', value=0.9, min=0, max=1, step=0.05),
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
                        value='st',
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
                        value='ow',
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
                    dcc.Input(id="input-box-7", className='input-box', type="text", value='1:1', list='negsamp-opts'),
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
            dcc.Input(id="input-box-8", className='input-box', type="text",
                      placeholder="Insert network names separated with blanks..."),
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
        ),
    ]),
    html.Br(),
    html.Div(id='network-labelpaths-div'),
    html.Br(),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label(['Network types:']),
                    dcc.RadioItems(
                        options=[
                            {'label': 'Directed', 'value': 'dir'},
                            {'label': 'Undirected', 'value': 'undir'},
                        ],
                        value='undir',
                        style={'display': 'grid'}
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    html.Label(['Separator per edgelist file:']),
                    dcc.Input(id="input-box-10", className='input-box', type="text",
                              placeholder="Insert separators with banks..."),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    html.Label(['Comment char per edgelist file:']),
                    dcc.Input(id="input-box-11", className='input-box', type="text",
                              placeholder="Insert comment chars with banks..."),
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
                        options=[
                            {'label': 'Relabel nodes (0..N)', 'value': 'rel'},
                            {'label': 'Remove selfloops', 'value': 'selfloops'},
                        ],
                        value=['rel', 'selfloops'],
                        style={'display': 'grid'}
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    dcc.Checklist(
                        options=[
                            {'label': 'Save network', 'value': 'save'},
                            {'label': 'Write stats', 'value': 'stats'},
                        ],
                        style={'display': 'grid'}
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
                    dcc.Input(id="input-prep-delim", className='input-box', type="text", value='Comma',
                              list='delim-opts'),
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
                        options=[
                            {'label': 'Common Neighbours', 'value': 'cn'},
                            {'label': 'Jaccard Coefficient', 'value': 'jc'},
                            {'label': 'Adamic Adar', 'value': 'aa'},
                            {'label': 'Cosine Similarity', 'value': 'cs'},
                            {'label': 'Resource Allocation', 'value': 'ra'},
                            {'label': 'Preferential Attachment', 'value': 'pa'},
                        ],
                        style={'display': 'grid'}
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%'}
            ),
            html.Div(
                children=[
                    dcc.Checklist(
                        options=[
                            {'label': 'LHN Index', 'value': 'lhn'},
                            {'label': 'Topological Overlap', 'value': 'to'},
                            {'label': 'Random Prediction', 'value': 'rand'},
                            {'label': 'Katz exact', 'value': 'katz'},
                            {'label': 'Katz approx', 'value': 'katza'},
                            {'label': 'All Baselines', 'value': 'bl'},
                        ],
                        style={'display': 'grid'}
                    ),
                ],
                style={'width': '30%', 'padding-right': '5%', 'padding-top': '20px'}
            ),
            html.Div(
                children=[
                    html.Label(['Neighbourhood type:']),
                    dcc.Dropdown(
                        id='prepdelim-dropdown',
                        options=[{'label': 'In neighbourhood', 'value': 'in'},
                                 {'label': 'Out neighbourhood', 'value': 'out'},
                                 {'label': 'In-Out', 'value': 'inout'}],
                        value='inout',
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
                        value='auc',
                    ),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Scores to report:']),
                    dcc.Dropdown(
                        id='scores-dropdown',
                        value='all',
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
                        value='roc',
                    ),
                ],
                style={'width': '22%', 'padding-right': '4%'}
            ),
            html.Div(
                children=[
                    html.Label(['Precision@k values:']),
                    dcc.Input(id="input-box-12", className='input-box', type="text",
                              placeholder='K values for Prec@k (e.g. 1 10 100 1000)'),
                ],
                style={'width': '22%'}
            ),
        ],
        style={'display': 'flex'}
    ),
    html.Br(),
    html.Br(),
])


# Callbacks

@app.callback(Output('run-eval', 'className'),
              Output('run-eval', 'children'),
              Input('run-eval', 'n_clicks'))
def set_active(n_clicks):
    ctx = callback_context

    if not ctx.triggered or n_clicks is None:
        return ['btn btn-square btn-run', 'Run Evaluation']

    else:
        if int(n_clicks) % 2 == 0:
            # Start run
            return ['btn btn-square btn-run', 'Run Evaluation']
        else:
            # Stop run
            return ['btn btn-square btn-run btn-active', 'Stop Evaluation']


@app.callback(Output('output-box-5', 'children'),
              Input('input-box-5', 'value'))
def render_train_perc(frac):
    val = int(float(frac) * 100)
    return 'Train-test fraction ({}%):'.format(val)


@app.callback(Output('output-box-6', 'children'),
              Input('input-box-6', 'value'))
def render_valid_perc(frac):
    val = int(float(frac) * 100)
    return 'Train-valid. fraction ({}%):'.format(val)


@app.callback(Output('output-box-frace', 'children'),
              Input('input-box-frace', 'value'))
def render_nodepairs_perc(frac):
    val = float(frac) * 100
    return 'Node pairs to evaluate ({:4.1f}%):'.format(val)


@app.callback(Output('output-network-upload', 'children'),
              Input('upload-networks', 'contents'),
              State('upload-networks', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        return list_of_names


@app.callback([Output('output-fracs', 'children'),
               Output('exprep', 'children'),
               Output('task', 'style'),
               Output('exprep', 'style'),
               Output('output-fracs', 'style'),
               Output('ee', 'style'),
               Output('network-labelpaths-div', 'children'),
               Output('maximize-dropdown', 'options'),
               Output('maximize-dropdown', 'value'),
               Output('scores-dropdown', 'options')],
              [Input('task-dropdown', 'value')])
def render_content(task):
    if task == 'LP' or task == 'SP':
        return [[],
                [html.Label(['Experiment repetitions:']),
                dcc.Input(id="input-box-1", className='input-box', type="number", value=5, min=0)],
                {'width': '30%', 'padding-right': '5%'},
                {'width': '30%', 'padding-right': '5%'},
                {'width': '0%', 'padding-right': '0%'},
                {'width': '30%'},
                [],
                [{'label': 'AUC', 'value': 'auc'},
                 {'label': 'F-score', 'value': 'fscore'},
                 {'label': 'Precision', 'value': 'prec'},
                 {'label': 'Recall', 'value': 'rec'},
                 {'label': 'Accuracy', 'value': 'acc'},
                 {'label': 'Fallout', 'value': 'fall'},
                 {'label': 'Miss', 'value': 'miss'}],
                'auc',
                [{'label': 'All', 'value': 'all'},
                 {'label': 'AUC', 'value': 'auc'},
                 {'label': 'F-score', 'value': 'fscore'},
                 {'label': 'Precision', 'value': 'prec'},
                 {'label': 'Recall', 'value': 'rec'},
                 {'label': 'Accuracy', 'value': 'acc'},
                 {'label': 'Fallout', 'value': 'fall'},
                 {'label': 'Miss', 'value': 'miss'}],
                ]
    elif task == 'NR':
        return [[html.Div(id='output-box-frace'),
                dcc.Input(id='input-box-frace', type='range', value=0.001, min=0, max=0.5, step=0.001)],
                [],
                {'width': '30%', 'padding-right': '5%'},
                {'width': '0%', 'padding-right': '0%'},
                {'width': '30%', 'padding-right': '5%'},
                {'width': '30%'},
                [],
                [{'label': 'AUC', 'value': 'auc'},
                 {'label': 'F-score', 'value': 'fscore'},
                 {'label': 'Precision', 'value': 'prec'},
                 {'label': 'Recall', 'value': 'rec'},
                 {'label': 'Accuracy', 'value': 'acc'},
                 {'label': 'Fallout', 'value': 'fall'},
                 {'label': 'Miss', 'value': 'miss'}],
                'auc',
                [{'label': 'All', 'value': 'all'},
                 {'label': 'AUC', 'value': 'auc'},
                 {'label': 'F-score', 'value': 'fscore'},
                 {'label': 'Precision', 'value': 'prec'},
                 {'label': 'Recall', 'value': 'rec'},
                 {'label': 'Accuracy', 'value': 'acc'},
                 {'label': 'Fallout', 'value': 'fall'},
                 {'label': 'Miss', 'value': 'miss'}],
                ]
    elif task == 'NC':
        return [[html.Label('Fractions of train nodes (%):'),
                 dcc.Input(id='input-box-fracn', className='input-box', type='text', value='10, 50, 90')],
                [html.Label(['Repetitions per node frac.:']),
                 dcc.Input(id="input-box-1", className='input-box', type="number", value=5, min=0)],
                {'width': '22%', 'padding-right': '4%'},
                {'width': '22%', 'padding-right': '4%'},
                {'width': '22%', 'padding-right': '4%'},
                {'width': '22%'},
                [html.Label(['Network node label paths:']),
                 dcc.Textarea(
                     id='network-nodelabels',
                     placeholder='Insert network node label file paths, one per line...',
                     style={
                         'width': '100%',
                         'height': '100px',
                     },
                 )],
                [{'label': 'F1-micro', 'value': 'f1_micro'},
                 {'label': 'F1-macro', 'value': 'f1_macro'},
                 {'label': 'F1-weighted', 'value': 'f1_weighted'}],
                'f1_micro',
                [{'label': 'All', 'value': 'all'},
                 {'label': 'F1-micro', 'value': 'f1_micro'},
                 {'label': 'F1-macro', 'value': 'f1_macro'},
                 {'label': 'F1-weighted', 'value': 'f1_weighted'}],
                ]


@app.callback(Output('method', 'children'),
              Output('add-method', 'n_clicks'),
              Input('add-method', 'n_clicks'),
              Input('delete-method', 'n_clicks'),
              State('method', 'children'),
              State('add-method', 'n_clicks'))
def add_method(val, delete, children, n_clicks):

    # Get callback context to detect which button triggered it
    ctx = callback_context
    if not ctx.triggered:
        if val:
            el = get_method_div(val)
            children.extend(el)
            return children, val
        else:
            raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'add-method':
            el = get_method_div(val)
            children.extend(el)
            return children, val

        elif button_id == 'delete-method':
            children = children[:-3]
            return children, n_clicks - 1

        else:
            raise PreventUpdate


def get_method_div(val):
    el = [
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
                                    id='splitalg-dropdown-{}'.format(val),
                                    options=[
                                        {'label': 'OpenNE', 'value': 'opne'},
                                        {'label': 'GEM', 'value': 'gem'},
                                        {'label': 'KarateClub', 'value': 'kk'},
                                        {'label': 'Other', 'value': 'other'}],
                                    value='other',
                                ),
                            ],
                            style={'width': '22%', 'padding-right': '4%'}
                        ),
                        html.Div(
                            children=[
                                html.Label(['Method name:']),
                                dcc.Input(id='name-m-{}'.format(val), className='input-box', type='text',
                                          placeholder="Insert method name..."),
                            ],
                            style={'width': '22%', 'padding-right': '4%'}
                        ),
                        html.Div(
                            children=[
                                html.Label(['Embedding type:']),
                                dcc.Dropdown(
                                    id='negsamp-dropdown-{}'.format(val),
                                    options=[{'label': 'Node embedding', 'value': 'ne'},
                                             {'label': 'Edge embedding', 'value': 'ee'},
                                             {'label': 'End to end', 'value': 'e2e'}],
                                    value='ne',
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
                                    style={'display': 'grid'}
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
                                  placeholder="Insert cmd call (e.g. ./venv/bin/python main.py --input {} --output {} --dim {})"),
                    ],
                ),
                html.Br(),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Label(['Tune hyperparameters:']),
                                dcc.Input(id='tune-m-{}'.format(val), className='input-box', type="text",
                                          placeholder="Insert hyperparameters to tune (e.g. --p 0.5 1 --q 1 2)"),
                            ],
                            style={'width': '48%', 'padding-right': '4%'}
                        ),
                        html.Div(
                            children=[
                                html.Label(['Input delimiter:']),
                                dcc.Input(id="input-method-delim", className='input-box', type="text",
                                          value='Comma', list='delim-opts'),
                            ],
                            style={'width': '22%', 'padding-right': '4%'}
                        ),
                        html.Div(
                            children=[
                                html.Label(['Output delimiter:']),
                                dcc.Input(id="output-method-delim", className='input-box', type="text",
                                          value='Comma', list='delim-opts'),
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
    return el
