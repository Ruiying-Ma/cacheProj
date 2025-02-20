import os
import json
import re
import subprocess
import logging_config
import logging
import traceback
from openbox import space as sp
from openbox import Optimizer
from datetime import datetime

LIBCACHSIM_PATH="/home/v-ruiyingma/libCacheSim" # /absolute/path/to/libCacheSim


def write_to_file(dest_path: str, contents, is_append=False, is_json=False):
    '''
    `dest_path`: absolute path
    '''
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    if is_append:
        assert is_json == False
        with open(dest_path, 'a') as file:
            file.write(contents)
    else:
        if is_json:
            assert dest_path.endswith(".json")
            with open(dest_path, 'w') as file:
                json.dump(contents, file, indent=4)
        else:
            with open(dest_path, 'w') as file:
                file.write(contents)

def extract_string(text: str, regex, group_id):
    match = re.search(regex, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(group_id)
    else:
        return None
    
def is_expr(text: str):
    return "=" in text and (all(c+"=" not in text for c in ["!", "=", "*", "+", "-", "/", "|", "%", '^']))

def get_type_and_value(text: str):
    if text.strip().lower() == 'true':
        return bool, True
    elif text.strip().lower() == 'false':
        return bool, False
    try:
        float(text)
        if "0." in text:
            return float, float(text)
        elif "." in text:
            return int, int(float(text))
        else:
            raise ValueError
    except ValueError:
        try:
            int(text)
            return int, int(text)
        except ValueError:
            return None
        
def modify_string(text: str, regex, group_id, modification):
    match = re.search(regex, text, re.DOTALL | re.MULTILINE)
    if match:
        modified_text = text[:match.start(group_id)] + str(modification) + text[match.end(group_id):]
        return modified_text
    return text

def run_libcachesim(cache_trace, cache_alg, cache_cap, params=""):
    '''
    Return miss ratio. `None` if fail.
    '''
    if params != "" and not params.startswith(" -e "):
        params = " -e " + params.strip()
    
    command = f'''{LIBCACHSIM_PATH}/_build/bin/cachesim {cache_trace} oracleGeneral {cache_alg} {cache_cap} --ignore-obj-size 1 --consider-obj-metadata 0 --warmup-sec -1 --report-interval 1000{params}'''
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            logging.warning(f"LibCacheSim Error\n\t[output] {result.stdout}\n\t[error] {result.stderr}")
            raise ValueError
        stdout = result.stdout
        result_lines = [l.strip() for l in stdout.split("\n") if len(l.strip()) > 0]
        result_info = result_lines[-1]
        miss_ratio_info = result_info.split(",")[2].strip()
        miss_ratio = float(miss_ratio_info.split()[2])
        return miss_ratio
    except Exception:
        logging.warning(f"Traceback:\n", traceback.format_exc())
        return None
    
def tune_libcachesim(trace, alg, cache_cap, fixed_default_params: bool=False, tune_runs: int=20):
    '''
    Return: default_mr, tuned_mr, default_params, tuned_params | `None`
    - `None`: fail to run libcachesim
    '''
    # map: param_name -> type, default, lower, uppper/type, default, choice
    m_trace_params = {
        "twoq": {
            "Ain-size-ratio": [float, 0.25, 0.0, 1.0],
            "Aout-size-ratio": [float, 0.5, 0.0, 1.0]
        },
        "slru": {
            "n-seg": [int, 4, 1, cache_cap],
            # seg-size
        },
        "RandomLRU": {
            "n-samples": [int, 16, 1, 64]
        },
        "tinyLFU": {
            "main-cache": [str, "SLRU", ["LRU", "SLRU", "LFU", "FIFO", "ARC", "clock", "SIEVE"]],
            "window-size": [float, 0.01, 0.0, 0.9999]
        },
        "fifomerge": {
            "retain-policy": [str, "freq", ["freq", "recency"]],
            "n-exam": [int, 100, 0, cache_cap],
            "ratio": [int, 2, 1, cache_cap],
        },
        "sfifo": {
            "n-seg": [int, 4, 1, cache_cap]
        },
        "sfifov0": {
            "n-queue": [int, 4, 1, cache_cap]
        },
        "lru-prob": {
            "prob": [float, 0.5, 0.0001, 1.0]
        },
        "s3lru": {
            "LRU-size-ratio": [float, 0.1, 0.0, 1.0],
            "main-cache": [str, "lru", ["lru", "clock", "clock2"]],
            "move-to-main-threshold": [int, 1, 0, cache_cap * 100 if trace != "MSR" else cache_cap * 10],
            "promote-on-hit": [int, 1, 0, 1]
        },
        "s3fifo": {
            "fifo-size-ratio": [float, 0.1, 0.0, 1.0],
            "move-to-main-threshold": [int, 1, 0, cache_cap * 100 if trace != "MSR" else cache_cap * 10]
        },
        "s3fifod": {
            "main-cache": [str, "clock2", ["FIFO", "clock", "clock2", "clock3", "sieve", "LRU", "ARC", "twoQ"]],
            "fifo-size-ratio": [float, 0.1, 0.0, 1.0],
            "move-to-main-threshold": [int, 1, 0, cache_cap * 100 if "MSR" not in trace else cache_cap * 10]
        },
        "lecar": {
            "update-weight": [int, 1, 0, 1],
            "lru-weight": [float, 0.5, 0, 1],
        },
        # "clock": {
        #     "n-bit-counter": [int, 1, 0, 63]
        # },
    }

    if fixed_default_params == True:
        for algo in m_trace_params:
            for param in m_trace_params[algo].values():
                if param[0] == int:
                    param[1] = 3
                elif param[0] == float:
                    param[1] = 0.42
                elif param[0] == bool:
                    param[1] = 1

    default_mr = run_libcachesim(trace, alg, cache_cap)
    if default_mr == None:
        return None
    
    if alg not in m_trace_params:
        return default_mr, default_mr, dict(), dict()
    
    default_params = {
        p: v[1]
        for p, v in m_trace_params[alg].items()
    }
        
    params_to_tune = []
    for param_name, param_status in m_trace_params[alg].items():
        param_type = param_status[0]
        if param_type == int:
            params_to_tune.append(sp.Int(name=param_name, lower=param_status[2], upper=param_status[3], default_value=param_status[1]))
        elif param_type == float:
            params_to_tune.append(sp.Real(name=param_name, lower=param_status[2], upper=param_status[3], default_value=param_status[1]))
        elif param_type == str:
            params_to_tune.append(sp.Categorical(name=param_name, choices=param_status[2], default_value=param_status[1]))
        else:
            raise ValueError('Unknown param type')
    space = sp.Space()
    space.add_variables(params_to_tune)

    def objective(config_space: sp.Configuration):
        params = dict(config_space).copy()
        if alg == "fifomerge":
            params["n-keep"] = max(params["n-exam"] // params["ratio"], 1)
            del params["ratio"]
        param_str = ""
        for param_name, param_val in params.items():
            if param_str != "":
                param_str += ","
            param_str += f"{param_name}={param_val}"

        miss_ratio = run_libcachesim(trace, alg, cache_cap, " -e " + param_str)
        if miss_ratio == None:
            miss_ratio = 1.0
        
        return dict(objectives=[miss_ratio])
    
    opt = Optimizer(
        objective_function=objective,
        config_space=space,
        num_objectives=1,
        num_constraints=0,
        max_runs=tune_runs,
        surrogate_type="prf",
        visualization="none"
    )

    tuned_mr = None
    tuned_params = None
    error_log = None
    try:
        history = opt.run()
    except Exception as error:
        error_log = f"Openbox Tuning Error: {repr(error)}\n" + traceback.format_exc()
        logging.warning(error_log)
        
    
    if error_log == None and len(history.get_incumbents()) > 0:
        tuned_mr = history.get_incumbent_value()
        tuned_params = dict(history.get_incumbent_configs()[0]).copy()

    
    if tuned_mr == None or tuned_mr > default_mr:
        tuned_mr = default_mr
        tuned_params = default_params

    return default_mr, tuned_mr, default_params, tuned_params
    
def miss_ratio_reduction(mr, fifo_mr):
    assert mr != 0.0
    assert fifo_mr != 0.0
    if mr > fifo_mr:
        return (fifo_mr - mr) / mr
    else:
        return (fifo_mr - mr) / fifo_mr
