import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pathlib import Path

from web_fiction_tracker.db_functions import *
from web_fiction_tracker.import_bookmarks_sql import *

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE= str(Path(app.root_path) / 'web_fiction_tracker.db'),
    SECRET_KEY='development key',
    USERNAME='ericonr',
    PASSWORD='oila1234'
))
app.config.from_envvar('WEB_FICTION_TRACKER_SETTINGS', silent=True)


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.cli.command('import')
def import_bookmarks():
    fiction_dict = import_b()
    fiction_ffnet_list = fiction_dict['ffnet']
    db = get_db()
    for fic in fiction_ffnet_list:
        fic.read_page()
        fic.find_nexts()
        input_db_ffnet(db, fic)
    db.commit()
    print('Imported bookmarks.')

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select * from entries')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    fic = fiction_ffnet((request.form['story_id'], request.form['chapter']), init=True)
    db.execute('select * from entries where id=?', str(fic.story))
    fetch_db = db.fetchone()
    if fetch_db == None:
        fic.read_page()
        fic.find_nexts()
    else:
        fic.verify_last(fetch_db['last_chapter_available'])

    input_db_ffnet(db, fic)
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))