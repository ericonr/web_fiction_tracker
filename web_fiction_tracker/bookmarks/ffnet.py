import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen
from functools import reduce

from web_fiction_tracker.bookmarks import *
from web_fiction_tracker.db_functions import *

class fiction_ffnet(fiction):
    base_link = 'https://m.fanfiction.net'
    def __init__(self, link, init=False, **kwargs):
        self.story, self.chapter = link

        link_suffix = '/s/' + self.story + '/' + str(self.chapter)

        fiction.__init__(self, link_suffix, init, **kwargs)

    def read_page(self):
        fiction.read_page(self)

        temp_list = [bold.string for bold in self.page.find_all('b') if 'FanFiction' not in str(bold.string)]
        if len(temp_list) == 0:
            self.exists = False
            self.title = 'Doesn\'t exist'
        else:
            self.exists = True
            self.title = temp_list[0]

        temp_list = [link['href'] for link in self.page.find_all('a') if 'Next' in str(link.string)]
        if len(temp_list) > 0:
            self._next_link = self.base_link + temp_list[0]
            self._has_next = True
        else:
            self._has_next = False

    def find_nexts(self):
        if self._has_next:
            self.next_chapter = fiction_ffnet((self.story, int(self.chapter)+1), init=True)

            if self.next_chapter._has_next:
                next_link_list, next_numb_list = self.next_chapter.find_nexts()
                next_numb_list.append(self.next_chapter.chapter)
                next_link_list.append(self.next_chapter.link)
            else:
                next_link_list = [self.next_chapter.link]
                next_numb_list = [self.next_chapter.chapter]

            del self.next_chapter
            self.next_chapter_link_list = next_link_list[:]
            self.next_chapter_link_list.reverse()
            self.next_chapter_numb_list = next_numb_list[:]
            self.next_chapter_numb_list.reverse()

            self.last_chapter_numb = self.next_chapter_numb_list[-1]
            self.next_chapter_numb = self.next_chapter_numb_list[0]
            self.next_chapter_link = self.next_chapter_link_list[0]

            return next_link_list, next_numb_list

        else:
            self.last_chapter_numb = self.chapter
            self.next_chapter_numb = self.chapter
            self.next_chapter_link = self.return_url(self.chapter)
            self.next_chapter_link_list = []
            self.next_chapter_numb_list = []
            return []

    def return_url(self, chapter):
        return self.base_link + '/s/' + self.story + '/' + str(chapter)

    def verify_last(self):
        verif = fiction_ffnet((self.story, int(self.last_chapter_numb)), init=True)
        verif.find_nexts()

        return verif.last_chapter_numb

    def show(self):
        return True
        if self.chapter != self.next_chapter_numb:
            return True
        else:
            return False