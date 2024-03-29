from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
		abort, render_template, flash
from contextlib import closing
import datetime

#config
DATABASE = '/tmp/flasktry.db'
DEBUG = True
SECRET_KEY = 'hihi'
USERNAME = 'root'
PASSWORD  = 'hehehe'

#create app
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

def round_date(delta):
	if delta.seconds > 0:
		return delta.days + 1
	else:
		return delta.days

def get_days_left(end_date):
	date_format = "%d-%m-%Y"
	today = datetime.datetime.today()
	return round_date(datetime.datetime.strptime(end_date, date_format) - today)

@app.route('/')
def show_tasks():
	query = "select task, startdate, enddate, priority from tasks order by priority desc"
	cur = g.db.execute(query)
	tasks = [dict(task=row[0], start=row[1], end=row[2], priority=row[3], \
			diff=get_days_left(row[2]))\
			for row in cur.fetchall()]
	return render_template('show_tasks.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
	if not session.get('logged_in'):
		abort(401)
	query = "insert into tasks (task, startdate, enddate, priority) values (?, ?, ?, ?)"
	g.db.execute(query, [request.form['task'], request.form['start'], request.form['end'], request.form['priority']])
	g.db.commit()
	flash("New task was successfully posted")
	return redirect(url_for('show_tasks'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid passwrd'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_tasks'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_tasks'))


if __name__ == "__main__":
	app.run()
