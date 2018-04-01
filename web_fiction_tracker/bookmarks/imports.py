import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen
from functools import reduce

from web_fiction_tracker.db_functions import *
from web_fiction_tracker.bookmarks import *

def import_b():
    with open(str(Path(app.root_path) / 'bookmarks.html'), 'r') as file:
        lines = file.read()
        page = BeautifulSoup(lines, 'html.parser')

    for index, header in enumerate(page.find_all('h3')):
        if 'Continuarao' in header.string:
            header_c = header

    division = header_c.find_next('dl')

    links_ffnet = [link['href'].split('/')[4:6] for link in division.find_all('a') if 'fanfiction.net' in link['href']]

    fiction_ffnet_list = [fiction_ffnet(link) for link in links_ffnet]
    fiction_dict = {'ffnet':fiction_ffnet_list}

    return fiction_dict

def import_bookmarks_ffnet(db):
    fiction_dict = import_b()
    fiction_ffnet_list = fiction_dict['ffnet']
    
    length = len(fiction_ffnet_list)
    for index, fic in enumerate(fiction_ffnet_list):
        fic.read_page()
        fic.find_nexts()
        if fic.exists:
            input_db_ffnet(db, fic, 'main')
        progress(index,length)
    db.commit()
    print('Imported bookmarks.')