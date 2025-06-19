#!/usr/bin/env python3

"""Datasette runner"""
import time
import json
import re
import sys
import traceback
import pathlib
from os import sep, mkdir
from os.path import dirname, exists
import logging


APP_TMT = 60
LOG_START_TIME = re.sub(r"\W+", "_", str(time.ctime()))
LOG_FMT_STRING = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

if getattr(sys, 'frozen', False):
    app_path = dirname(sys.executable)
    app_name = pathlib.Path(sys.executable).stem
    APP_RUNMODE = 'PROD'
    time.sleep(APP_TMT)
else:
    app_path = os.path.dirname(os.path.abspath("__file__"))
    app_name = pathlib.Path(__file__).stem
    APP_RUNMODE = 'TEST'
LOG_DIR = f'{app_path}{sep}logs'

if not exists(LOG_DIR):
    mkdir(LOG_DIR)
LOG_FILENAME = f'{LOG_DIR}{sep}{app_name}_{LOG_START_TIME}.log'
log_handlers = [logging.StreamHandler(),logging.FileHandler(LOG_FILENAME)]


logger = logging.getLogger(APP_RUNMODE)
logging.basicConfig(format=LOG_FMT_STRING,
                    datefmt='%d.%m.%Y %H:%M:%S',
                    level=logging.INFO, # NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL
                    handlers=log_handlers)

try:
    with open(f"{app_path}{sep}{app_name}.config", 'r', encoding='UTF-8') as cf:
        conf = json.load(cf)
except Exception as ex: # pylint: disable=broad-exception-caught
    logger.critical("Config file problem - %s", str(ex))
    sys.exit()
db_path = conf['db_path']

def run_datasette(in_db_path):
    """Simple datasette runner"""
    r_d_db_path = in_db_path
    try:
        cmd = f"datasette serve {r_d_db_path} -h 0.0.0.0 -p 8001"
        os.system(cmd)
    except Exception as ex: # pylint: disable=broad-exception-caught
        logger.info('Datasette run failed with exception %s', str(ex))
    return True


while True:
    try:
        logger.info('Try datasette with database directory %s', db_path)
        run_datasette(db_path)
        logger.info('Everything is OK with DB %s', db_path)
    except Exception as ex: # pylint: disable=broad-exception-caught
        logger.warning(str(ex))
        logger.warning(traceback.format_exc())
        time.sleep(3)
        continue
