#!/usr/bin/env python3

import requests
from logs.compound_log import CompoundLogger
from logs.file_log import FileLogger
from logs.log import Logger
from logs.sample_log import SampleLogger
from logs.terminal_log import TerminalLogger
import settings
import sys
from db import database
from bs4 import BeautifulSoup
from threading import Thread

db = database.backend

custom_headers = {
    'User-Agent': settings.user_agent,
}

def get_url_links(url):
    """
    Scrape the links from a URL.
    """
    req = requests.get(url, verify=False, headers=custom_headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    soup_links = soup.find_all('a')
    links = []
    for link in soup_links:
        link = link.get('href')
        if type(link) is not str:
           print('dead link object:' + str(link))
           continue
        if not is_good_filetype(link):
            continue
        full_link = get_full_url(url, link)
        if len(url) >= len(full_link):
            continue
        links.append(full_link)
    return links

def scrape_url(logger: Logger, id: int, url: str, passovers: list[str] = [], origional_url: str = ':::'):
    """
    Scrape the links from a URL and update the database accordingly.
    """
    if url in passovers:
        logger.log("Passing over " + str(id) + ": " + url)
    else:
        logger.log("Scraping " + str(id) + ": " + url)
        if origional_url == ':::':
            origional_url = url
        for link in get_url_links(url):
            if link.endswith('/'):
                try:
                    scrape_url(logger, id, link, passovers, origional_url)
                except requests.exceptions.ConnectionError:
                    logger.log("Failed to scrape " + str(id) + ": " + link)
            else:
                db.save_url(id, link)
                logger.log("Saved " + str(id) + ": " + link)
        if url == origional_url:
            db.update_scrape_stamp(id)
            logger.log("Done with source " + str(id))

def is_good_filetype(url: str):
    if '..' in url or \
            url.startswith('?'):
        return False

    if url.endswith('/'):
        return True
    
    if len(settings.extensions) == 0:
        return True
    
    lurl = url.lower()
    extension = lurl.split('.')[-1]
    if extension in settings.extensions:
        return True
    return False

def get_full_url(page, link):
    if not page.endswith('/'):
        page = page + '/'
    if link.startswith('./'):
        link = link[2:]

    if link.startswith('http'):
        return link
    if link.startswith('/'):
        protocol, remainder = page.split('://')
        if link.startswith('//'):
            return protocol + ':' + link
        domain = remainder.split('/')[0]
        return protocol + '://' + domain + link
    return page + link

def full_scrape(source_id=-1, logger: Logger=FileLogger('scrape')):
    force = source_id != -1
    def scrape_single(id: int, url: str, age: int, enabled: bool):
        id = int(id)
        age = int(age)
        logger.log("Starting " + str(id) + ": " + url)
        if not force and age < settings.min_age:
            logger.log("Scape too recent, skipping " + url)
            return
        passovers = db.get_passovers(id, url)
        db.purge_source(id)
        logger.log("Cleared " + str(id))
        try:
            scrape_url(logger, id, url, passovers)
        except requests.exceptions.ConnectionError:
            logger.log("Failed to scrape " + str(id) + ": " + url)
    db.for_each_source(source_id, scrape_single)
    db.commit()

class Scraper:
    thread: (Thread | None)

    def __init__(self, logger: (Logger|None)):
        self.sample_logger = SampleLogger(10)
        if logger == None:
            self.logger = self.sample_logger
        else:
            self.logger = CompoundLogger()
            self.logger.add_log(self.sample_logger)
        self.source = -1
        self.thread = None

    def status(self):
        if self.thread != None and self.thread.is_alive():
            return 1
        return 0
    
    def start(self, source=-1) -> bool:
        if self.thread != None and self.thread.is_alive():
            return False
        self.sample_logger.reset()
        self.source = source
        self.thread = Thread(target=full_scrape, args=(source, self.logger))
        self.thread.start()
        return True
    
    def sample(self) -> str:
        return self.sample_logger.get_sample()

if __name__ == '__main__':
    count = len(sys.argv)
    logger = CompoundLogger()
    logger.add_log(TerminalLogger())
    logger.add_log(FileLogger('scrape'))
    if count > 1:
        target = sys.argv[1]
        if target.isdigit():
            full_scrape(int(target), logger)
        else:
            pass
    else:
        full_scrape(-1, logger)
