#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021

from evalne_gui.app import app
from dash.dependencies import Input, Output
from dash import dcc, State, html
from evalne_gui.settings import settings_layout
from evalne_gui.results import results_layout
from evalne_gui.dashboard import dashboard_layout
from evalne_gui.monitoring import monitoring_layout


app.layout = html.Div([

    # Header div
    html.Div(children=[

        # Title
        html.H1(
            children='EvalNE-GUI',
            style={'textAlign': 'center',
                   'text-shadow': '4px 4px 5px #020202'}
        ),

        # Subtitle
        html.H2(
            children='A Python library for evaluating network embedding methods.',
            style={'textAlign': 'center',
                   'text-shadow': '2px 2px 3px #020202',
                   'font-weight': '700'}
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
            persistence=True,
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
                    label='Runs & Results',
                    value='results',
                    className='custom-tab results-tab',
                    selected_className='custom-tab--selected'
                ),
                dcc.Tab(
                    label='Settings',
                    value='settings',
                    className='custom-tab settings-tab',
                    selected_className='custom-tab--selected'
                ),
            ]),
        html.Div(id='tabs-content-classes', className='tabs-content')
    ], style={'display': 'flex', 'position': 'absolute', 'min-height': '100%', 'width': '100%'}),
], style={'margin': 0, 'padding': 0, 'flex': 1})


# --------------------------
#         Callbacks
# --------------------------

@app.callback([Output('tabs-header', 'children'),
              Output('tabs-content-classes', 'children')],
              [Input('main-tabs', 'value')])
def render_content(tab):
    """ Renders the page content based on the tab selected by the user. """

    if tab == 'dashboard':
        return html.Div([
            html.H3('Dashboard', className='header-title')
        ]), dashboard_layout
    elif tab == 'monitoring':
        return html.Div([
            html.H3('Monitoring', className='header-title')
        ]), monitoring_layout
    elif tab == 'results':
        return html.Div([
            html.H3('Runs & Results', className='header-title')
        ]), results_layout
    elif tab == 'settings':
        return html.Div([
            html.H3('Settings', className='header-title')
        ]), settings_layout
