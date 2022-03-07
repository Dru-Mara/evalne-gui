import io
import os
import shlex
import psutil
import base64
import configparser
import numpy as np
from subprocess import Popen
from collections import OrderedDict


def start_process(cmd, cwd=None, verbose=True):
    """
    Runs the cmd command provided as input in a new process.

    Parameters
    ----------
    cmd : string
        A string indicating the command to run on the command line.
    cwd : string
        The working directory for the new process spawned.
    verbose : bool
        Boolean indicating if the execution output should be shown or not (pipes stdout and stderr to devnull).

    Examples
    --------
    Runs a command that prints Start, sleeps for 5 seconds and prints Done

    >>> util.run("python -c 'import time; print(\"Start\"); time.sleep(5); print(\"Done\")'", True)
    Start
    Done

    """
    if cwd is None:
        cwd = os.getcwd()
    if verbose:
        sto = None
        ste = None
    else:
        devnull = open(os.devnull, 'w')
        sto = devnull
        ste = devnull

    Popen(shlex.split(cmd), stdout=sto, stderr=ste, cwd=cwd)
    print('EvalNE process started!')


def stop_process(process_name):
    """ Stops a process using the process name. """
    proc = search_process(process_name)
    if proc is not None:
        proc.kill()
        print('EvalNE process killed!')


def search_process(process_name):
    """ Searches for a running process with the provided name. """
    for proc in psutil.process_iter():
        if process_name in shlex.join(proc.cmdline()):
            return proc
    return None


def import_config_file(contents, filename):
    # Parse the contents of the input file
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    conf = io.StringIO(decoded.decode('utf-8'))

    #from evalne.evaluation.pipeline import EvalSetup
    #setup = EvalSetup(conf)

    # Create a configparser and read the file
    config = configparser.ConfigParser()
    config.read_file(conf)

    print(config.get('GENERAL', 'task'))

    conf_vals = OrderedDict({'task-dropdown': config.get('GENERAL', 'task'),
                             'ee-dropdown': getlist('GENERAL', 'edge_embedding_methods', str),
                             'ib-exprep': config.getint('GENERAL', 'lp_num_edge_splits'),
                             'ib-frace': config.getfloat('GENERAL', 'nr_edge_samp_frac'),
                             'ib-rpnf': config.getint('GENERAL', 'nc_num_node_splits'),
                             'ib-fracn': config.get('GENERAL', 'nc_node_fracs'),
                             'ib-lpmodel': config.get('GENERAL', 'lp_model'),
                             'ib-embdim': config.get('GENERAL', 'embed_dim'),       # process
                             'ib-timeout': config.getint('GENERAL', 'timeout'),     # process
                             'ib-seed': config.get('GENERAL', 'seed'),              # process
                             'ib-trainfrac': config.getfloat('EDGESPLIT', 'traintest_frac'),
                             'ib-validfrac': config.getfloat('EDGESPLIT', 'trainvalid_frac'),
                             'splitalg-dropdown': config.get('EDGESPLIT', 'split_alg'),
                             'negsamp-dropdown': 'ow' if config.getboolean('EDGESPLIT', 'owa') else 'cw',
                             'ib-negratio': config.get('EDGESPLIT', 'fe_ratio'),
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
                             'baselines-checklist': getlist('BASELINES', 'lp_baselines', str),      # TODO! how to split this
                             'baselines-checklist2': getlist('BASELINES', 'lp_baselines', str),     # TODO! how to split this
                             'neighbourhood-dropdown': config.get('BASELINES', 'neighbourhood'),
                             'maximize-dropdown': config.get('REPORT', 'maximize'),
                             'scores-dropdown': config.get('REPORT', 'scores'),
                             'curves-dropdown': config.get('REPORT', 'curves'),
                             'ib-precatk': config.get('REPORT', 'precatk_vals')})

    method_vals = OrderedDict({'m-lib-dropdown': 'other',
                               'm-name': '',
                               'm-type-dropdown': 'ne',
                               'm-opts': ['dir'],
                               'm-cmd': '',
                               'm-tune': '',
                               'm-input-delim': '',
                               'm-output-delim': ''})

    return 0


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
        aux = [str(int(val) / 100) for val in conf_dict['ib-fracn'].split()]
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
