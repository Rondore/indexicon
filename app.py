#!/usr/bin/env python3

from db.db_backend import DbBackend
from logs.file_log import FileLogger
import util
import settings
import html
from flask import Flask, render_template
from db import database
from scrape import Scraper
from markupsafe import escape
from flask import request
from urllib.parse import unquote
from os import path

app = Flask(__name__, static_url_path = settings.internal_base_url + 'static')

scraper = Scraper(FileLogger('scrape'))

def header(page_name: str, extra_elements: list[str] = []) -> str:
    """
    Get the html header content for a page
    """
    full_title = settings.name
    if len(page_name) > 0:
        full_title += ' - ' + page_name
    theme_css = ''
    #theme_css = '<link rel="stylesheet" type="text/css" href="<?= $public_theme_dir ?>style.css">'
    extras = ''
    tab = ''
    for element in extra_elements:
        extras += tab + element + '\n'
        tab = '    '
    return '''<html>
    <head>
        <title>''' + full_title + '''</title>
        <base href="''' + settings.public_base_url + '''">
        <link rel="stylesheet" type="text/css" href="static/style.css">
        ''' + theme_css + '''
        <meta name="viewport" content="width=device-width, minimum-scale=1.0, maximum-scale=1.0">
    ''' + extras + '''
    </head>
    <body>'''

def footer() -> str:
    """
    Get the html footer content for a page
    """
    return '''    </body>
</html>'''

menu_items = [
    ["", "Search", 'home'],
    ["admin", "Sources", 'admin']
]

def nav() -> str:
    """
    Get the html content for the navigation bar
    """
    current = request.endpoint or ''
    output = '<nav>'
    for url, name, funct in menu_items:
        current_class = ''
        if current == funct:
            current_class = ' current'
        output += f'<a href="%s" class="menu-item%s">%s</a>'%(url, current_class, name)
    output += '</nav>'
    return output

def scrape_hud() -> str:
    status = scraper.status()
    text_status = 'Ready'
    if status > 0:
        text_status = 'Scraping ID ' + str(scraper.queue[0])
    elif status == -1:
        text_status = 'Scraping all sources'
    sample = ''
    if status != 0:
        sample = scraper.sample()
    return render_template('scrape_hud.html', text_status=text_status, scrape_status=status, sample=sample)

def source_table(db: DbBackend) -> str:
    total = 0
    entries = ''
    status = scraper.status()
    def add_entry(id: int, url: str, age: int, enabled: bool, count: int):
        nonlocal total
        nonlocal entries
        total += count
        pretty_age = util.pretty_age(age)
        if pretty_age != 'never':
            pretty_age += ' ago'
        entries += render_template('source_table_entry.html', id=id, url=url, age=pretty_age, enabled=enabled, count=count, running=id in scraper.queue)
    db.for_each_source_with_count(-1, add_entry, False)
    return render_template('source_table.html', count=util.format_number(total), entries=entries)

def passover_table(db: DbBackend) -> str:
    entries = ''
    def add_entry(id: int, url: str, directory: str):
        nonlocal entries
        entries += render_template('passover_table_entry.html', id=id, url=url, directory=directory)
    db.for_each_passover(-1, add_entry, False)
    return render_template('passover_table.html', entries=entries)

@app.route(settings.internal_base_url)
def home():
    db = database.get_db()
    search_content = ''
    search = request.args.get('search', '')
    encoded_search = str(escape(search))
    if len(search) > 0:
        def get_search_entry_html(name: str, file: str, source_url: str):
            dirty_name = unquote(name)
            dirty_source = unquote(source_url)
            nonlocal search_content
            search_content += render_template('search_result.html', dirty_name=dirty_name, link_url=file, file_name=name, dirty_source=dirty_source, source_url=source_url)
        count = db.search_db(search, get_search_entry_html)
        if count > 0:
            search_content = '<div class="result-header">Found ' + str(count) + ' files</div>' + search_content
            search_content += search_other(search)
    output = header('')
    output += render_template('search.html', indexicon_name=settings.name, results = encoded_search)
    output += nav()
    output += search_content
    output += footer()
    db.close()
    return output

def start_scrape(raw_id: str):
    if raw_id.isdigit():
        id = int(raw_id)
    else:
        id = -1
    start = scraper.scrape(id)
    if start:
        return 'Started Scrape'
    return 'Scrape of source already in progress'

def add_source(url: str, db: DbBackend):
    db.add_source(url)
    return 'Added source ' + html.escape(url)

def add_passover(url: str, db: DbBackend):
    if not url.startswith('http'):
        return 'Please include the full URL'
    if not url.endswith('/'):
        url += '/'
    db.add_passover(url)
    return 'Added passover ' + html.escape(url)

def delete_source(raw_id: str, db: DbBackend):
    id = int(raw_id)
    url = db.delete_source(id)
    return 'Deleted source ' + html.escape(url)

def delete_passover(raw_id: str, db: DbBackend):
    id = int(raw_id)
    source_url, directory = db.delete_passover(id)
    url = source_url + directory
    return 'Deleted passover ' + html.escape(url)

def enable_source(raw_id: str, db: DbBackend):
    id = int(raw_id)
    db.enable_source(id)
    return 'Enabled ' + str(id)

def disable_source(raw_id: str, db: DbBackend):
    id = int(raw_id)
    db.disable_source(id)
    return 'Disabled ' + str(id)

def process_admin_post(form, db: DbBackend) -> str:
    if 'scrape' in form:
        return start_scrape(form['scrape'])
    elif 'addition' in form:
        return add_source(form['addition'], db)
    elif 'passover-addition' in request.form:
        return add_passover(form['passover-addition'], db)
    elif 'delete' in form:
        return delete_source(form['delete'], db)
    elif 'passover-delete' in request.form:
        return delete_passover(form['passover-delete'], db)
    elif 'enable' in form:
        return enable_source(form['enable'], db)
    elif 'disable' in form:
        return disable_source(form['disable'], db)
    return ''

@app.route(settings.internal_base_url + "admin", methods=['GET', 'POST'])
def admin():
    db = database.get_db()
    output = ''
    action_message = ''
    if request.method == 'POST':
        action_message = process_admin_post(request.form, db)
    output = header('Admin', ['<link rel="stylesheet" type="text/css" href="static/fonts/font-awesome.css">'])
    output += '<h1>' + settings.name + ' Admin</h1>'
    output += nav()
    output += scrape_hud()
    if len(action_message) > 0:
        output += '<div class="action-message">' + action_message + '</div><br>'
    output += source_table(db)
    output += passover_table(db)
    output += footer()
    db.close()
    return output

def search_other_default(raw_search: str) -> str:
    plus_search = raw_search.replace(' ', '+').replace('"', '\"')
    google_search = "https://www.google.com/search?udm=14&q=" + plus_search
    return render_template('search_other.html', google_search=google_search)

search_other = search_other_default



# Initialize addon directory init script if missing
addon_init_path = 'addon/__init__.py'
if path.isdir('addon/') and not path.isfile(addon_init_path):
    with open(addon_init_path, 'w+') as output:
        with open('default_files/example_addon_init.py', 'r') as input:
            for line in input.readlines():
                output.write(line)

# Import addon python files
from addon import *