#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mara Alexandru Cristian
# Contact: alexandru.mara@ugent.be
# Date: 22/03/2021

import io
import os
import shlex
import psutil
import base64
import datetime
import configparser
import numpy as np
from subprocess import Popen, run
from collections import OrderedDict
from evalne_gui.procinfo import EvalneProc
from evalne_gui.init_values import init_vals


def get_ui_proc():
    return EvalneProc(psutil.Process())


def get_evalne_proc():
    p = search_process('-m evalne')
    return EvalneProc(p)


def search_process(process_name):
    """ Searches for a running process with the provided name. """
    for proc in psutil.process_iter():
        if process_name in shlex.join(proc.cmdline()):
            return proc
    return None


def evalne_installed(exec_path):
    cmd = "{} -c 'import evalne;'".format(exec_path)
    res = True
    try:
        devnull = open(os.devnull, 'w')
        run(shlex.split(cmd), stdout=devnull, stderr=devnull, check=True)
    except:
        res = False

    return res


def import_config_file(contents):
    """ Imports data from a config file. For options that are left blank, default values are used. """
    # Parse the contents of the input file
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    conf = io.StringIO(decoded.decode('utf-8'))

    # Create a configparser and read the file
    config = configparser.ConfigParser()
    config.read_file(conf)

    return config


def get_config_vals(contents):
    """ Reads an input conf file and returns the values found as a list. Does not return NE method related values. """
    # Read the config file
    config = import_config_file(contents)

    # Parse baselines
    bl_1, bl_2 = parse_bl(config.get('BASELINES', 'lp_baselines'))

    conf_vals = OrderedDict({'task-dropdown': config.get('GENERAL', 'task'),
                             'ee-dropdown': parse_list(
                                 config.get('GENERAL', 'edge_embedding_methods'), init_vals['ee-dropdown']),
                             'ib-exprep': parse_val(
                                 config.get('GENERAL', 'lp_num_edge_splits'), init_vals['ib-exprep'], int),
                             'ib-frace': parse_val(
                                 config.get('GENERAL', 'nr_edge_samp_frac'), init_vals['ib-frace'], float),
                             'ib-rpnf': parse_val(
                                 config.get('GENERAL', 'nc_num_node_splits'), init_vals['ib-rpnf'], int),
                             'ib-fracn': config.get('GENERAL', 'nc_node_fracs'),
                             'ib-lpmodel': config.get('GENERAL', 'lp_model'),
                             'ib-embdim': parse_val(
                                 config.get('GENERAL', 'embed_dim'), init_vals['ib-embdim'], int),
                             'ib-timeout': parse_val(
                                 config.get('GENERAL', 'timeout'), init_vals['ib-timeout'], int),
                             'ib-seed': parse_val(
                                 config.get('GENERAL', 'seed'), init_vals['ib-seed'], int),
                             'ib-trainfrac': parse_val(
                                 config.get('EDGESPLIT', 'traintest_frac'), init_vals['ib-trainfrac'], float),
                             'ib-validfrac': parse_val(
                                 config.get('EDGESPLIT', 'trainvalid_frac'), init_vals['ib-validfrac'], float),
                             'splitalg-dropdown': config.get('EDGESPLIT', 'split_alg'),
                             'negsamp-dropdown': 'ow' if config.getboolean('EDGESPLIT', 'owa') else 'cw',
                             'ib-negratio': '1:1' if config.get('EDGESPLIT', 'fe_ratio') == ''
                             else '{}:1'.format(config.get('EDGESPLIT', 'fe_ratio')),
                             'ib-nwnames': config.get('NETWORKS', 'names'),
                             'network-paths': config.get('NETWORKS', 'inpaths'),
                             'network-nodelabels': config.get('NETWORKS', 'labelpaths'),
                             'network-types': 'dir' if config.getboolean('NETWORKS', 'directed') else 'undir',
                             'ib-separator': config.get('NETWORKS', 'separators'),
                             'ib-comment': config.get('NETWORKS', 'comments'),
                             'nw-prep-checklist': ['rel' if config.getboolean('PREPROCESSING', 'relabel') else '',
                                                   'selfloops' if config.getboolean('PREPROCESSING', 'del_selfloops') else ''],
                             'nw-prep-checklist2': ['save' if config.getboolean('PREPROCESSING', 'save_prep_nw') else '',
                                                    'stats' if config.getboolean('PREPROCESSING', 'write_stats') else ''],
                             'input-prep-delim': config.get('PREPROCESSING', 'delimiter'),
                             'baselines-checklist': bl_1,
                             'baselines-checklist2': bl_2,
                             'neighbourhood-dropdown': config.get('BASELINES', 'neighbourhood'),
                             'maximize-dropdown': config.get('REPORT', 'maximize'),
                             'scores-dropdown': config.get('REPORT', 'scores'),
                             'curves-dropdown': config.get('REPORT', 'curves'),
                             'ib-precatk': config.get('REPORT', 'precatk_vals')})

    return [val for val in conf_vals.values()]


def get_config_methods(contents):
    """ Reads an input config file and returns the NE method parameter values as a list. """
    # Read the config file
    config = import_config_file(contents)

    num_other_methods = len(config.get('OTHER METHODS', 'names_other').split())
    tune_params = pop_empty_line(config.get('OTHER METHODS', 'tune_params_other').split('\n'))
    tune_params.extend([''] * (num_other_methods - len(tune_params)))

    method_vals = OrderedDict({'m-lib-dropdown': ['other'] * num_other_methods,
                               'm-name': config.get('OTHER METHODS', 'names_other').split(),
                               'm-type-dropdown': config.get('OTHER METHODS', 'embtype_other').split(),
                               'm-opts': parse_opts(config.get('OTHER METHODS', 'write_weights_other'),
                                                    config.get('OTHER METHODS', 'write_dir_other')),
                               'm-cmd': pop_empty_line(config.get('OTHER METHODS', 'methods_other').split('\n')),
                               'm-tune': tune_params,
                               'm-input-delim': config.get('OTHER METHODS', 'input_delim_other').split(),
                               'm-output-delim': config.get('OTHER METHODS', 'output_delim_other').split()})

    # Add the opne methods
    num_opne_methods = len(config.get('OPENNE METHODS', 'names_opne').split())
    tune_opne = pop_empty_line(config.get('OPENNE METHODS', 'tune_params_opne').split('\n'))
    tune_opne.extend([''] * (num_opne_methods - len(tune_opne)))

    method_vals['m-lib-dropdown'].extend(['opne'] * num_opne_methods)
    method_vals['m-name'].extend(config.get('OPENNE METHODS', 'names_opne').split())
    method_vals['m-type-dropdown'].extend(['ne'] * num_opne_methods)
    method_vals['m-opts'].extend([('', '') for val in range(num_opne_methods)])
    method_vals['m-cmd'].extend(pop_empty_line(config.get('OPENNE METHODS', 'methods_opne').split('\n')))
    method_vals['m-tune'].extend(tune_opne)
    method_vals['m-input-delim'].extend([' '] * num_opne_methods)
    method_vals['m-output-delim'].extend([' '] * num_opne_methods)

    return [val for val in method_vals.values()]


def pop_empty_line(lst):
    if lst[-1] == '':
        return lst[:-1]
    return lst


def get_num_methods(contents):
    """ Reads an input config file and returns the number of NE methods. """
    # Read the config file
    config = import_config_file(contents)
    num_methods = len(config.get('OTHER METHODS', 'names_other').split()) + \
                  len(config.get('OPENNE METHODS', 'names_opne').split())
    return num_methods


def parse_opts(str_weights, str_dir):
    """ Parses config file strings and returns a list of tuples for write weights and write dir. """
    l1 = str_weights.lower().split()
    l2 = str_dir.lower().split()
    if len(l1) == 0:
        res = []
    else:
        for i in range(len(l1)):
            l1[i] = 'weights' if l1[i] == 'true' else ''
            l2[i] = 'dir' if l1[i] == 'true' else ''
    res = list(zip(l1, l2))
    return res


def parse_bl(str_val):
    """ Parse the baselines string into two lists with the appropriate methods. If katz includes a numerical value
     it will also add that as a method which is incorrect. """
    lst = str_val.split()
    lst1 = []
    lst2 = []
    for l in lst:
        if 'common' in l or 'jaccard' in l or 'adamic' in l or 'cosine' in l or 'resource' in l or 'preferential' in l:
            lst1.append(l)
        else:
            lst2.append(l)
    return lst1, lst2


def parse_val(str_val, default_val, dtype):
    """ Parses a string as the specified type or returns a default value if string is empty. """
    if str_val == '' or str_val.lower() == 'none':
        res = default_val
    else:
        res = dtype(str_val)
    return res


def parse_list(str_list, default_val, dtype=str):
    """ Parses a string as a list of objects of given type. A default values is returned if the string is empty. """
    lst = str_list.split()
    if len(lst) == 0 or lst[0] == '' or lst[0] == 'None':
        res = default_val
    else:
        res = list(map(dtype, lst))
    return res


def export_config_file(conf_path, conf_dict, methods_dict):
    """ Creates an EvalNE config file and populates options with the provided input values. """
    # Split method dict in opne and non-opne methods
    opne_dict, other_dict = split_method_types(methods_dict)

    config = configparser.ConfigParser()
    config.optionxform = str
    config['GENERAL'] = {'TASK': conf_dict['task-dropdown'],
                         'LP_NUM_EDGE_SPLITS': get_edge_splits(conf_dict),
                         'NC_NUM_NODE_SPLITS': conf_dict['ib-rpnf'] if conf_dict['task-dropdown'] == 'nc' else '',
                         'NC_NODE_FRACS': get_node_fracs(conf_dict),
                         'NR_EDGE_SAMP_FRAC': conf_dict['ib-frace'] if conf_dict['task-dropdown'] == 'nr' else '',
                         'EDGE_EMBEDDING_METHODS': '' if conf_dict['task-dropdown'] == 'nc'
                         else get_list(conf_dict['ee-dropdown'], ' '),
                         'LP_MODEL': conf_dict['ib-lpmodel'],
                         'EMBED_DIM': conf_dict['ib-embdim'],
                         'TIMEOUT': '' if conf_dict['ib-timeout'] == 0 else conf_dict['ib-timeout'],
                         'VERBOSE': 'False',
                         'SEED': conf_dict['ib-seed']}
    config['NETWORKS'] = {'NAMES': conf_dict['ib-nwnames'],
                          'INPATHS': conf_dict['network-paths'],
                          'DIRECTED': 'True' if conf_dict['network-types'] == 'dir' else 'False',
                          'SEPARATORS': conf_dict['ib-separator'],
                          'COMMENTS': conf_dict['ib-comment'],
                          'LABELPATHS': conf_dict['network-nodelabels']}
    config['PREPROCESSING'] = {'RELABEL': 'True' if 'rel' in conf_dict['nw-prep-checklist'] else 'False',
                               'DEL_SELFLOOPS': 'True' if 'selfloops' in conf_dict['nw-prep-checklist'] else 'False',
                               'SAVE_PREP_NW': 'True' if 'save' in conf_dict['nw-prep-checklist2'] else 'False',
                               'WRITE_STATS': 'True' if 'stats' in conf_dict['nw-prep-checklist2'] else 'False',
                               'DELIMITER': conf_dict['input-prep-delim']}
    config['EDGESPLIT'] = {'TRAINTEST_FRAC': conf_dict['ib-trainfrac'],
                           'TRAINVALID_FRAC': conf_dict['ib-validfrac'],
                           'SPLIT_ALG': conf_dict['splitalg-dropdown'],
                           'OWA': 'True' if conf_dict['negsamp-dropdown'] == 'ow' else 'False',
                           'FE_RATIO': float(conf_dict['ib-negratio'].split(':')[0])}
    config['BASELINES'] = {'LP_BASELINES': get_list(conf_dict['baselines-checklist']+conf_dict['baselines-checklist2'],
                                                    '\n'),
                           'NEIGHBOURHOOD': conf_dict['neighbourhood-dropdown']}
    config['OPENNE METHODS'] = opne_dict
    config['OTHER METHODS'] = other_dict
    config['REPORT'] = {'MAXIMIZE': conf_dict['maximize-dropdown'],
                        'SCORES': conf_dict['scores-dropdown'],
                        'CURVES': '' if conf_dict['curves-dropdown'] == 'none' else conf_dict['curves-dropdown'],
                        'PRECATK_VALS': conf_dict['ib-precatk']}
    with open(conf_path, 'w') as configfile:
        config.write(configfile)


def get_node_fracs(conf_dict):
    """ For NC tasks converts % of train nodes to a fraction in [0-1). Returns an empty string for other tasks. """
    if conf_dict['task-dropdown'] == 'nc':
        aux = []
        for val in conf_dict['ib-fracn'].split():
            if int(val) > 1.0:
                aux.append(str(int(val) / 100))
            else:
                aux.append(val)
        res = ' '.join(aux)
    else:
        res = ''
    return res


def get_edge_splits(conf_dict):
    """ Returns the number of experiment repeats for LP and SP tasks and an empty string for the rest. """
    if conf_dict['task-dropdown'] == 'nc' or conf_dict['task-dropdown'] == 'nr':
        res = ''
    else:
        res = conf_dict['ib-exprep']
    return res


def get_list(lst, joinchar):
    """ Given a list of values and a separator character returns a string representation of the list. """
    return '' if len(lst) == 0 else joinchar.join(lst)


def split_method_types(methods_dict):
    """ Given a dict of confing method parameters and values returns two dicts for OpenNE and non-OpenNE methods."""
    if len(methods_dict['m-lib-dropdown']) == 0:
        # No methods to evaluate
        opne_dict = {'NAMES_OPNE': '', 'METHODS_OPNE': '', 'TUNE_PARAMS_OPNE': ''}
        other_dict = {'NAMES_OTHER': '', 'EMBTYPE_OTHER': '', 'WRITE_WEIGHTS_OTHER': '', 'WRITE_DIR_OTHER': '',
                      'METHODS_OTHER': '', 'TUNE_PARAMS_OTHER': '', 'INPUT_DELIM_OTHER': '', 'OUTPUT_DELIM_OTHER': ''}
    else:
        # Ignore methods where name and cmd call are empty
        empty_name = np.array(methods_dict['m-name']) == ''
        empty_cmd = np.array(methods_dict['m-cmd']) == ''
        ignore = empty_name * empty_cmd

        if np.sum(ignore) == len(methods_dict['m-lib-dropdown']):
            # No methods to evaluate
            opne_dict = {'NAMES_OPNE': '', 'METHODS_OPNE': '', 'TUNE_PARAMS_OPNE': ''}
            other_dict = {'NAMES_OTHER': '', 'EMBTYPE_OTHER': '', 'WRITE_WEIGHTS_OTHER': '', 'WRITE_DIR_OTHER': '',
                          'METHODS_OTHER': '', 'TUNE_PARAMS_OTHER': '', 'INPUT_DELIM_OTHER': '',
                          'OUTPUT_DELIM_OTHER': ''}
        else:
            # Get indices of opne methods
            isopne = np.array(methods_dict['m-lib-dropdown']) == 'opne'
            mask = isopne * ~ignore
            invmask = ~isopne * ~ignore

            # Fill the opne dict
            opne_dict = {'NAMES_OPNE': get_list(np.array(methods_dict['m-name'])[mask], ' '),
                         'METHODS_OPNE': get_list(np.array(methods_dict['m-cmd'])[mask], '\n'),
                         'TUNE_PARAMS_OPNE': get_list(np.array(methods_dict['m-tune'])[mask], '\n')}

            # Fill the others dict
            other_dict = {'NAMES_OTHER': get_list(np.array(methods_dict['m-name'])[invmask], ' '),
                          'EMBTYPE_OTHER': get_list(np.array(methods_dict['m-type-dropdown'])[invmask], ' '),
                          'WRITE_WEIGHTS_OTHER': proc_nested_lists('weights',
                                                                   np.array(methods_dict['m-opts'], dtype=object)[invmask]),
                          'WRITE_DIR_OTHER': proc_nested_lists('dir',
                                                               np.array(methods_dict['m-opts'], dtype=object)[invmask]),
                          'METHODS_OTHER': get_list(np.array(methods_dict['m-cmd'])[invmask], '\n'),
                          'TUNE_PARAMS_OTHER': get_list(np.array(methods_dict['m-tune'])[invmask], '\n'),
                          'INPUT_DELIM_OTHER': get_list(np.array(methods_dict['m-input-delim'])[invmask], ' '),
                          'OUTPUT_DELIM_OTHER': get_list(np.array(methods_dict['m-output-delim'])[invmask], ' ')}

    return opne_dict, other_dict


def proc_nested_lists(val, lst):
    """ Given an input list of lists and value returns a string of True/False indicating if val is in a sublist. """
    res = []
    for l in lst:
        res.append(str(val in l))
    return get_list(res, ' ')


def get_logged_evals(path):
    res = []
    for fname in sorted(os.listdir(path), reverse=True):
        aux = []
        if '_eval_' in fname:
            # Get filename
            aux.append(fname)

            fpath = os.path.join(path, fname)
            logpath = os.path.join(fpath, 'eval.log')
            with open(logpath) as f:
                content = f.read()
                content = content.strip().split('\n')
                # Get status
                if 'Evaluation end' in content[-1]:
                    aux.append('Finished')
                else:
                    if len(res) == 0 and get_evalne_proc().running():
                        aux.append('Running')
                    else:
                        aux.append('Failed')
                # Get runtime
                start_time = content[0].split(' - ')[0]
                end_time = content[-1].split(' - ')[0]
                std = datetime.datetime.strptime(start_time, '%d-%m-%y %H:%M:%S')
                etd = datetime.datetime.strptime(end_time, '%d-%m-%y %H:%M:%S')
                aux.append(str(etd - std))

                # Get start time
                aux.append(start_time)

                # Get end time
                aux.append(end_time)
            res.append(aux)
    return res


def read_file(path, filename, console=False):
    try:
        f = open(os.path.join(path, filename), 'r')
        text = f.read()
        f.close()
        return text
    except FileNotFoundError:
        if console:
            return 'Output not found! Start an evaluation to monitor its output...'
        else:
            return 'File not found! Evaluation is still running or has failed...'
