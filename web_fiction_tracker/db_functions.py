import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pathlib import Path

from flask import current_app as app

def progress(index, length):
    print(str(index+1) + '/' + str(length))

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def input_db_ffnet(db, fic, folder):
    if fic.exists:
        db.execute('insert into fiction_ffnet (id, title, first_chapter_link, chapter, next_chapter_numb, next_chapter_link, last_chapter_numb, hidden, folder) values (?,?,?,?,?,?,?,?,?)',
            [fic.id, fic.title, fic.first_chapter_link, fic.chapter, fic.next_chapter_numb, fic.next_chapter_link, fic.last_chapter_numb, False, fic.folder])