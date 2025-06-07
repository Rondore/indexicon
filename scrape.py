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

db = database.get_db()

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

class Scraper:
    thread: (Thread | None)
    queue: list[int]
    logger: Logger

    def __init__(self, logger: (Logger|None)):
        self.sample_logger = SampleLogger(10)
        if logger == None:
            self.logger = self.sample_logger
        else:
            self.logger = CompoundLogger()
            self.logger.add_log(self.sample_logger)
        self.thread = None
        self.queue = []

    def status(self):
        if self.thread != None and self.thread.is_alive():
            return 1
        return 0
    
    def start(self) -> bool:
        if self.thread != None and self.thread.is_alive():
            return False
        self.sample_logger.reset()
        self.thread = Thread(target=_run_scrape, args=(self,))
        self.thread.start()
        return True
    
    def sample(self) -> str:
        return self.sample_logger.get_sample()
    
    def add_source(self, id: int) -> bool:
        addon_ids = []
        if id == -1:
            for source_id in db.get_due_source_ids():
                addon_ids.append(source_id)
        else:
            addon_ids.append(id)
        added = False
        for source_id in addon_ids:
            if source_id not in self.queue:
                self.queue.append(source_id)
                added = True
        return added

    def scrape(self, id: int) -> bool:
        added = False
        added = self.add_source(id)
        if self.thread is None or not self.thread.is_alive():
            self.start()
        return added

def _run_scrape(scraper: Scraper):
    while len(scraper.queue) > 0:
        target_id = scraper.queue[0]
        url, age, enabled = db.get_source_info(target_id)
        scraper.logger.log("Starting " + str(id) + ": " + url)
        passovers = db.get_passovers(target_id, url)
        db.purge_source(target_id)
        scraper.logger.log("Cleared " + str(target_id))
        try:
            scrape_url(scraper.logger, target_id, url, passovers)
        except requests.exceptions.ConnectionError:
            scraper.logger.log("Failed to scrape " + str(target_id) + ": " + url)
        scraper.queue.remove(target_id)
        db.commit()

if __name__ == '__main__':
    count = len(sys.argv)
    logger = CompoundLogger()
    logger.add_log(TerminalLogger())
    logger.add_log(FileLogger('scrape'))
    scrape_id = -2
    if count > 1:
        target = sys.argv[1]
        if target.isdigit():
            scrape_id = int(target)
        else:
            pass
    else:
        scrape_id = -1
    if scrape_id != -2:
        scraper = Scraper(logger)
        scraper.scrape(scrape_id)
        if scraper.thread:
            scraper.thread.join()