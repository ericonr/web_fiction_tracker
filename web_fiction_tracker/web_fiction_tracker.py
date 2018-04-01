import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pathlib import Path

from web_fiction_tracker.db_functions import *
from web_fiction_tracker.bookmarks import *

from contextlib import closing

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

global_dict = {'type':'all', 'hide_update':True, 'hide_hidden':True}

#cli_commands

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
    db = get_db()
    import_bookmarks_ffnet(db)


#routes - make add and refresh threaded

@app.route('/')
def show_entries():
    db = get_db()

    if global_dict['type'] == 'fiction_ffnet' or global_dict['type'] == 'all':
        cur = db.execute('select * from fiction_ffnet')
        temp_list = cur.fetchall()

        entries = []
        for element in temp_list:
            fic = fiction_ffnet((element['id'], element['chapter']), next_numb=element['next_chapter_numb'])
            if fic.show(global_dict['hide_update']) and not element['hidden']:
                element = dict(element)
                element['table'] = 'fiction_ffnet'
                entries.append(element)

    return render_template('show_entries.html', entries=entries, hides=global_dict)

@app.route('/refresh', methods=['POST'])
def refresh():
    db = get_db()

    #fiction_ffnet table
    cur = db.execute('select * from fiction_ffnet')
    temp_list = cur.fetchall()
    length = len(temp_list)

    for index, element in enumerate(temp_list):
        fic = fiction_ffnet((element['id'], element['chapter']), next_numb=element['next_chapter_numb'], last_numb=element['last_chapter_numb'])
        fic.verify_last()
        if fic.last_chapter_numb != element['last_chapter_numb']:
            db.execute('update fiction_ffnet set last_chapter_numb=? where id=?', [fic.last_chapter_numb, fic.id])
        progress(index, length)
    db.commit()
    flash('Data refreshed')

@app.route('/filter', methods=['POST'])
def choose_what_to_show():
    if 'hide_update' in request.form.keys():
        global_dict['hide_update'] = True
    else:
        global_dict['hide_update'] = False
    if 'hide_hidden' in request.form.keys():
        global_dict['hide_hidden'] = True
    else:
        global_dict['hide_hidden'] = False
    global_dict['type'] = request.form['type']

    return redirect(url_for('show_entries'))

@app.route('/entry_hide/<table>/<entry>')
def entry_hide(table, entry):
    db = get_db()

    if 'hide' in request.form.keys():
        hide = True
    else:
        hide = False

    db.execute('update ? set hidden=? where id=?', [table, hide, entry])
    db.commit()

    return redirect(url_for('show_entries'))

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    
    if request.form['type'] == 'fiction_ffnet':

        #cursor = db.cursor()
        cursor = db.execute('select * from fiction_ffnet where id=?', [request.form['story_id']])
        fetch_db = cursor.fetchone()

        if fetch_db == None:
            fic = fiction_ffnet((request.form['story_id'], request.form['chapter']), init=True)
            fic.read_page()
            fic.find_nexts()
            input_db_ffnet(db, fic, 'main')
            db.commit()
            flash('New entry was successfully posted')
        else:
            flash('Entry already exists')
            pass

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