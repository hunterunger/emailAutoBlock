"""

// Epic widgets //

Originally from my AI stock trading bot repo.

"""

import datetime
import json
import os
from time import sleep
import yaml


class Style:
    green = "\u001b[38;5;121m"
    blue = "\u001b[38;5;117m"
    red = "\u001b[38;5;198m"
    yellow = "\u001b[38;5;228m"
    white = "\u001b[38;5;255m"
    black = "\u001b[38;5;234m"
    bold = "\u001b[1m"
    underline = "\u001b[4m"
    inverted = "\u001b[7m"
    reset = "\u001b[0m"


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def easy_read(filename, filetype="TXT"):
    if filetype == "TXT":
        with open(filename, mode="r") as f:  # update program job
            return f.read()
    elif filetype == "JSON":
        with open(filename) as f:  # update program job
            return json.load(f)
    else:
        print("error. Filetype '%s' not found." % filetype)


def easy_write(filename, write_data, filetype="TXT"):
    if filetype == "TXT":
        with open(filename, mode="w") as f:
            f.write(write_data)
    elif filetype == "JSON":
        with open(filename, mode="w", encoding='utf-8') as f:
            json.dump(write_data, f, ensure_ascii=False, indent=4, default=str)
    else:
        print("error. Filetype '%s' not found." % filetype)


def sleep_time_until_checkpoint(minute_break):
    """
    Returns the time until the next checkpoint. E.g. if the current minute is 10, and the checkpoint is 15,
    the function will return 5.
    
    :param minute_break:
    :return:
    """
    now_second = datetime.datetime.now().second
    now_minute = datetime.datetime.now().minute
    
    if 60 / minute_break == float(60 // minute_break):
        next_break = 0
        while now_minute >= next_break:
            next_break += minute_break
        
        return (next_break - now_minute) * 60 - now_second
    else:
        return (60 - now_minute) * 60


def wait_indicator(time_to_wait):
    # fun spinning loading indicator for terminal
    loading_icon = ['|', '/', '-', '\\']
    for i in range(time_to_wait * 5):
        print(' ' + loading_icon[i % 4] + ' ', end='\r', flush=True)
        sleep(0.2)


def config(set_to: dict = None):
    """
    Get or set the config file.
    :param set_to: The config file to set to.
    :return:
    """
    
    if set_to:
        with open('config files/config.yml', 'w') as f:
            yaml.dump(set_to, f)
    else:
        with open('config files/config.yml', 'r') as stream:
            return yaml.safe_load(stream)
