#!/usr/bin/env python3

import scrape
import wget
import os
import requests
import sys
from urllib.parse import unquote
from util import is_docker

def full_download(url, destination=':::', filter_filetypes=True):
    print('Scraping ' + url)
    if destination == ':::':
        destination = os.getcwd()
    for link in scrape.get_url_links(url, filter_filetypes):
        print('Found link ' + link)
        if link.endswith('/'):
            folder_name = link.split('/')[-2]
            print('Folder name: ' + folder_name)
            target_destination = destination + '/' + unquote(folder_name) + '/'
            if not os.path.exists(target_destination):
                os.makedirs(target_destination)
            try:
                full_download(url + folder_name, target_destination)
            except requests.exceptions.ConnectionError:
                print("Failed to scrape " + url)
        else:
            file_name = link.split('/')[-1]
            source = unquote(url + '/' + file_name)
            target = os.path.realpath(destination + '/' + unquote(file_name))
            print('Downloading ' + source + ' to ' + target)
            try:
                wget.download(source, target)
            except Exception as e:
                print("Failed to download " + link)
                if hasattr(e, 'message'):
                    print(e.message) # type: ignore
                else:
                    print(e)

if __name__ == '__main__':
    count = len(sys.argv)
    if count > 1:
        target = ''
        arg_position = 0
        arg_index = 1
        filter_filetypes = True
        destination = ':::'
        if is_docker and os.path.isdir('download'):
            destination = 'download/'
        while(len(sys.argv) > arg_index):
            argument = sys.argv[arg_index]
            if(argument.startswith('--')):
                flag = argument[2:]
                if flag.lower() == 'all-files':
                    filter_filetypes = False
            else:
                match(arg_position):
                    case 0:
                        target = argument
                    case 1:
                        destination = argument
                arg_position += 1
            arg_index += 1
        full_download(target, destination, filter_filetypes)
    else:
        pass