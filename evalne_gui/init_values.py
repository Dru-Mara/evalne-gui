#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021

from collections import OrderedDict

init_vals = OrderedDict({'task-dropdown': 'lp',
                         'ee-dropdown': ['average'],
                         'ib-exprep': 5,
                         'ib-frace': 0.001,
                         'ib-rpnf': 5,
                         'ib-fracn': '10 50 90',
                         'ib-lpmodel': 'LogisticRegressionCV',
                         'ib-embdim': 128,
                         'ib-timeout': 0,
                         'ib-seed': 42,
                         'ib-trainfrac': 0.8,
                         'ib-validfrac': 0.9,
                         'splitalg-dropdown': 'spanning_tree',
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
                         'input-prep-delim': '',
                         'baselines-checklist': [],
                         'baselines-checklist2': [],
                         'neighbourhood-dropdown': 'in out',
                         'maximize-dropdown': 'auroc',
                         'scores-dropdown': 'all',
                         'curves-dropdown': 'roc',
                         'ib-precatk': ''})

method_init_vals = OrderedDict({'m-lib-dropdown': 'other',
                                'm-name': '',
                                'm-type-dropdown': 'ne',
                                'm-opts': ['dir'],
                                'm-cmd': '',
                                'm-tune': '',
                                'm-input-delim': '',
                                'm-output-delim': ''})

init_settings = OrderedDict({'ib-pythonpath': '',
                             'ib-evalpath': ''})
