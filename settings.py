#!/usr/bin/env python3

from os import path
from util import environment_variable, environment_variable_list

# Set default values

db_type = 'sqlite'
db_db = 'indexicon'
db_user = 'indexicon'
db_password = 'bad_password'
db_host = 'local.db'

name = 'Indexicon'
internal_base_url = "/"
public_base_url = internal_base_url
scrape_log = 'data/scrape.log'
min_age = 604800 # 86400 seconds = 1 day, 604800 seconds = 1 week
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0'

extensions = []

# Allow user to set values from data/settings.py

if path.isfile('data/settings.py'):
    from data import settings as user_settings

# Environment variables have the last say

db_type = environment_variable('DB_TYPE', db_type)
db_db = environment_variable('DB_DB', db_db)
db_user = environment_variable('DB_USER', db_user)
db_password = environment_variable('DB_PASSWORD', db_password)
db_host = environment_variable('DB_HOST', db_host)

name = environment_variable('NAME', name)
internal_base_url = environment_variable('INTERNAL_URL', internal_base_url)
public_base_url = environment_variable('PUBLIC_URL', public_base_url)
scrape_log = environment_variable('LOG', scrape_log)
min_age = int(environment_variable('MIN_AGE', str(min_age)))
user_agent = environment_variable('USER_AGENT', user_agent)

extensions = environment_variable_list('EXTENSIONS', extensions)