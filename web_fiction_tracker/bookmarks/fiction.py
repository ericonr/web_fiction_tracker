import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen
from functools import reduce

from web_fiction_tracker.db_functions import *

class fiction():
    def __init__(self, link, init=False, **kwargs):
        self.link = self.base_link + link
        self.next_chapter_link_list = []
        self.next_chapter_numb_list = []
        self.title = ''

        self.first_chapter_link = self.return_url(1)
        self.folder = 'main'

        if init:
            self.read_page()

        if 'next_numb' in kwargs.keys():
            self.next_chapter_numb = kwargs['next_numb']
            self.next_chapter_link = self.return_url(self.next_chapter_numb)
        if 'last_numb' in kwargs.keys():
            self.last_chapter_numb = kwargs['last_numb']
        
    def read_page(self):
        self.page = BeautifulSoup(urlopen(self.link), 'html.parser')

    #for debug
    def __str__(self):
        if len(self.next_chapter_numb_list) > 0:
            temp_str = reduce((lambda x,y: str(x)+', '+str(y)), self.next_chapter_numb_list)
        else:
            temp_str = 'up to date'
        return self.title + ': ' + str(temp_str)