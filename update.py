import logging
from os import path as ospath, environ
from subprocess import run as srun
from requests import get as rget
from dotenv import load_dotenv
from pymongo import MongoClient
from web.log_config import configure_logger

configure_logger()
LOGGER = logging.getLogger(__name__)

if ospath.exists('info.log'):
    with open('info.log', 'r+') as f:
        f.truncate(0)
                    
if 'CONFIG_ENV' in environ:
    LOGGER.info("CONFIG_ENV variable found! Downloading config file ...")
    download_config_file = srun(["curl", "-sL", f"{environ.get('CONFIG_ENV')}", "-o", "config.env"])
    if download_config_file.returncode == 0:
        LOGGER.info("Config file downloaded as 'config.env'")
    else:
        LOGGER.error("Something went wrong while downloading config file! please recheck the CONFIG_ENV variable")

load_dotenv('config.env', override=True)

try:
    if bool(environ.get('_____REMOVE_THIS_LINE_____')):
        LOGGER.error('The README.md file there to be read! Exiting now!')
        exit()
except:
    pass

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    LOGGER.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = BOT_TOKEN.split(':', 1)[0]

DATABASE_URL = environ.get('DATABASE_URL', '')
if len(DATABASE_URL) == 0:
    DATABASE_URL = None
    
DATABASE_NAME = environ.get('DATABASE_NAME', '')
if len(DATABASE_NAME) == 0:
    DATABASE_NAME = 'MLTB'

if DATABASE_URL is not None:
    conn = MongoClient(DATABASE_URL)
    db = conn[DATABASE_NAME]
    if config_dict := db.settings.config.find_one({'_id': bot_id}):  #retrun config dict (all env vars)
        environ['UPSTREAM_REPO'] = config_dict['UPSTREAM_REPO']
        environ['UPSTREAM_BRANCH'] = config_dict['UPSTREAM_BRANCH']
    conn.close()

UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
   UPSTREAM_REPO = None

UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'

if UPSTREAM_REPO is not None:
    if ospath.exists('.git'):
        srun(["rm", "-rf", ".git"])

    update = srun([f"git init -q \
                     && git config --global user.email admin@culturecloud.gq \
                     && git config --global user.name culturecloud \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)

    if update.returncode == 0:
        LOGGER.info(f'Successfully updated with latest commit from {UPSTREAM_REPO} ({UPSTREAM_BRANCH})')
    else:
        LOGGER.error('Something went wrong while updating, check UPSTREAM_REPO if valid or not!')