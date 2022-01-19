import os
import dash
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from dash import dcc, State, html
from dash.html.Label import Label

runs_layout = html.Div([

    html.H3(children='Logged evaluation runs', className='section-title'),
    html.Hr(className='sectionHr'),
    html.Br(),

    # TODO

])
