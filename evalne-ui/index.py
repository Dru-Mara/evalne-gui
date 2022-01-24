# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import webbrowser
from threading import Timer
from app import app
from dash.dependencies import Input, Output
from dash import dcc, State, html
from runs import runs_layout
from results import results_layout
from dashboard import dashboard_layout
from monitoring import monitoring_layout


def open_browser():
    port = 8050
    webbrowser.open_new("http://localhost:{}".format(port))


app.layout = html.Div([

    # Header div
    html.Div(children=[

        # Title
        html.H1(
            children='EvalNE Dashboard',
            style={'textAlign': 'center',
                   'text-shadow': '4px 4px 5px #020202'
            }
        ),

        # Subtitle
        html.H2(
            children='A Python library for evaluation network embedding methods.',
            style={'textAlign': 'center',
                   'text-shadow': '2px 2px 3px #020202',
                   'font-weight': '700'
            }
        ),
        html.Br(),
        html.Br()
    ], style={'padding': 10, 'flex': 1, 'backgroundColor': '#161a1d'}),

    # Tab header
    html.Div(className='row', children=[
        html.Div(className='empty', children='\u2770'),
        html.Div(id='tabs-header', className='tabs-head'),
    ]),

    # Sidebar and main div
    html.Div([
        dcc.Tabs(
            id="main-tabs",
            value='dashboard',
            vertical=True,
            parent_className='custom-tabs',
            className='custom-tabs-container',
            children=[
                dcc.Tab(
                    label='Dashboard',
                    value='dashboard',
                    className='custom-tab dashboard-tab',
                    selected_className='custom-tab--selected'
                ),
                dcc.Tab(
                    label='Monitoring',
                    value='monitoring',
                    className='custom-tab monitoring-tab',
                    selected_className='custom-tab--selected'
                ),
                dcc.Tab(
                    label='Runs',
                    value='runs',
                    className='custom-tab runs-tab',
                    selected_className='custom-tab--selected'
                ),
                dcc.Tab(
                    label='Results',
                    value='results',
                    className='custom-tab results-tab',
                    selected_className='custom-tab--selected'
                ),
            ]),
        html.Div(id='tabs-content-classes', className='tabs-content')
    ], style={'display': 'flex'}),
], style={'margin': 0, 'padding': 0, 'flex': 1})


@app.callback([Output('tabs-header', 'children'),
              Output('tabs-content-classes', 'children')],
              [Input('main-tabs', 'value')])
def render_content(tab):
    if tab == 'dashboard':
        return html.Div([
            html.H3('Dashboard', className='header-title')
        ]), dashboard_layout
    elif tab == 'monitoring':
        return html.Div([
            html.H3('Monitoring', className='header-title')
        ]), monitoring_layout
    elif tab == 'runs':
        return html.Div([
            html.H3('Runs', className='header-title')
        ]), runs_layout
    elif tab == 'results':
        return html.Div([
            html.H3('Results', className='header-title')
        ]), results_layout


if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=8050, host='localhost', use_reloader=False)
