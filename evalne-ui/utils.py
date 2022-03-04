import os
import shlex
import psutil
import configparser
import numpy as np
from subprocess import Popen


def start_process(cmd, verbose):
    """
    Runs the cmd command provided as input in a new process.

    Parameters
    ----------
    cmd : string
        A string indicating the command to run on the command line.
    verbose : bool
        Boolean indicating if the execution output should be shown or not (pipes stdout and stderr to devnull).

    Examples
    --------
    Runs a command that prints Start, sleeps for 5 seconds and prints Done

    >>> util.run("python -c 'import time; print(\"Start\"); time.sleep(5); print(\"Done\")'", True)
    Start
    Done

    """
    if verbose:
        sto = None
        ste = None
    else:
        devnull = open(os.devnull, 'w')
        sto = devnull
        ste = devnull

    Popen(shlex.split(cmd), stdout=sto, stderr=ste)
    print('EvalNE process started!')


def stop_process(process_name):
    proc = search_process(process_name)
    if proc is not None:
        proc.kill()
        print('EvalNE process killed!')


def search_process(process_name):
    for proc in psutil.process_iter():
        if process_name in shlex.join(proc.cmdline()):
            return proc
    return None


def export_config_file(conf_path, conf_dict, methods_dict):
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
    if conf_dict['task-dropdown'] == 'nc':
        aux = [str(int(val) / 100) for val in conf_dict['ib-fracn'].split()]
        res = ' '.join(aux)
    else:
        res = ''
    return res


def get_edge_splits(conf_dict):
    if conf_dict['task-dropdown'] == 'nc' or conf_dict['task-dropdown'] == 'nr':
        res = ''
    else:
        res = conf_dict['ib-exprep']
    return res


def get_list(lst, joinchar):
    return '' if len(lst) == 0 else joinchar.join(lst)


def split_method_types(methods_dict):

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
    res = []
    for l in lst:
        res.append(str(val in l))
    return get_list(res, ' ')
