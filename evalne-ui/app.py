# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import os
import dash
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from dash import dcc, State, html
from dash.html.Label import Label
from dashboard import dashboard_layout


external_stylesheets = [{
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
            html.H3('Dashboard')
        ]), dashboard_layout
    elif tab == 'monitoring':
        return html.Div([
            html.H3('Monitoring')
        ]), html.Div([
            html.H3('Monitoring content!')
        ])
    elif tab == 'runs':
        return html.Div([
            html.H3('Runs')
        ]), html.Div([
            html.H3('Runs content!')
        ])
    elif tab == 'results':
        return html.Div([
            html.H3('Results')
        ]), html.Div([
            html.H3('Results content!')
        ])


if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='0.0.0.0')
