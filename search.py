#!/t/www/private/venv/bin/python3

import sys
from db import database

db = database.backend

def conduct_search( unclean_search: str ):
    def print_search(name: str, file: str, source_url: str):
        print()
        print(name)
        print('(' + source_url + ') ')
        print(file)
    count = db.search_db(unclean_search, print_search)
    if count == 0:
        print("No results found")
    google_search = '+'.join(unclean_search).replace(' ', '+')
    google_search = google_search.replace('"', '\"')
    google_link = "https://www.google.com/search?q=" + google_search + "+intitle:\"index+of\"+(.mp4+OR+.mkv+OR+.mov+OR+.avi+OR+.m4v)"
    print("Still searching? Try " + google_link)

if __name__ == '__main__':
    count = len(sys.argv)
    if count > 1:
        conduct_search(' '.join(sys.argv[1:]))
    else:
        print("Enter your search term as arguments to the command.")
