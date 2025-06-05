#!/usr/bin/env python3

import scrape
import wget
import os
import requests
import sys

def full_download(url, destination=':::'):
    print('Scraping ' + url)
    if destination == ':::':
        destination = os.getcwd()
    for link in scrape.get_url_links(url):
        print('Found link ' + link)
        if link.endswith('/'):
            folder_name = link.split('/')[-2]
            print('Folder name: ' + folder_name)
            target_destination = destination + '/' + folder_name + '/'
            if not os.path.exists(target_destination):
                os.makedirs(target_destination)
            try:
                full_download(url + folder_name, target_destination)
            except requests.exceptions.ConnectionError:
                print("Failed to scrape " + url)
        else:
            file_name = link.split('/')[-1]
            source = url + file_name
            target = destination + file_name
            print('Downloading ' + source + ' to ' + target)
            wget.download(source, target)

if __name__ == '__main__':
    count = len(sys.argv)
    if count > 1:
        target = sys.argv[1]
        full_download(target)
    else:
        pass