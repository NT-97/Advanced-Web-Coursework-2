from flask import Flask,g, request,redirect, url_for, flash, render_template
from calendar import monthrange
from datetime import date, datetime, timedelta

import sqlite3

app = Flask(__name__)
app.secret_key = 'ewhj[a49fjq[in4pnja['
#where the database is stored
database_location = 'var/demonstratordb.db'
user = None
#get the database connection
def retrieveDatabase():
  db = getattr(g, 'db', None)
  if db is None:
    db = sqlite3.connect(database_location)
    g.db = db
   
    db.row_factory = sqlite3.Row
  return db
#query the database
def queryDatabase(query, args=(), one=False):
  cur = retrieveDatabase().execute(query, args)
  rv = cur.fetchall()
  cur.close()
  return (rv[0] if rv else None) if one else rv
#insert into db
def insertValues(table, values=()):
  cur = retrieveDatabase().cursor()
  query = 'INSERT OR REPLACE INTO %s VALUES (%s)' % (
    table,
    ', '.join(['?'] * len(values))
  )
  cur.execute(query, values)
  retrieveDatabase().commit()
  cur.close()
#delete row from db
def deleteRow(table, values=()):
  cur = retrieveDatabase().cursor()
  query = 'DELETE FROM %s WHERE day=? AND month=? AND year=? AND user=?' % (table)
  cur.execute(query, values)
  retrieveDatabase().commit()
  cur.close

#close connection when application is exited
@app.teardown_appcontext
def close_db_connection(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()
#intitialise the db for first time use 
def init_db():
  with app.app_context():
    db = retrieveDatabase()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
  # redirect to 404.html page
    return render_template('404.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
  global user
  if not user:
    if request.method == 'GET':
      return render_template('login.html')
    # If attempting to login, query credentials against database
    elif request.form['action'] == 'Login':
      sql = "SELECT * FROM users WHERE user=? AND password=?"
      # If not successful - try again
      if not queryDatabase(sql, [request.form['user'], request.form['password']], one=True):
        flash("Login failed, Please Try Again!!!")
        return render_template('login.html')
      # If successful - set the "user" variable
      else:
        user = request.form['user']
    # If registering new user
    else:
      # Add new user to the database
      insertValues('users', [request.form['user'], request.form['password'], 10.48])
      flash("New user added to database!!!")
  return redirect(url_for('root'))

#logout route
@app.route('/logout')
def logout():
  global user
  user = None
  return render_template('login.html')

#root of app
@app.route('/')
@app.route('/<int:year>/<int:month>', methods=['GET', 'POST'])
def root(year=None, month=None):

  if not user:
    #redirect user to login screen
    return redirect(url_for('login'))
# Setting today's date as the current date
  main = date.today()
  if year and month:
    main = main.replace(year=year, month=month)

  # Calculating the last day in the current month
  last_day = monthrange(main.year, main.month)[1]
  # Finding the next month by adding a day to the last day of the month
  following_month = main.replace(day=last_day) + timedelta(days=1)
    # Calculating the weekday of the first day
  first_weekday = monthrange(main.year, main.month)[0]
  # previouos month calculated by subtracting one from the first day of current month
  previous_month = main.replace(day=1) - timedelta(days=1)

  # Making changes to the calendar if the user POST'ed a request
  if request.method == 'POST':
    if request.form['action'] == 'Save':
      insertValues("classes", [request.form['day'], main.month, main.year,
      request.form['class_start'], request.form['class_end'], request.form['moduleID'],
      request.form['moduleName'], request.form['lecturer'],  user])
   
    else:
      deleteRow("classes", [request.form['day'], main.month, main.year, user])

  # Initialising a dictionary for storing days containing classes
  daysWithClasses = {}
  # Total number of classes
  classes = 0
  # Sum of hours worked
  total_hours = 0
  # Money made
  earned = 0

#query user details
  sql = "SELECT * FROM users WHERE user=?"
  userDetails = queryDatabase(sql, [user], one=True)

#searching classes for the current month
  sql = "SELECT day, class_start, class_end FROM classes WHERE year=? AND month=? AND user=?"
  for row in queryDatabase(sql, [main.year, main.month, user]):
    classes += 1
    formatTime = '%H:%M'
    #calculate duration of class
    duration = datetime.strptime(row['class_end'], formatTime) - datetime.strptime(row['class_start'], formatTime)
    #round the duration
    duration_rounded = duration.total_seconds() / 3600.0
    total_hours += duration_rounded
    #added to total earnings
    earned += userDetails['pay'] * duration_rounded
    daysWithClasses[row['day']] = {'class_start': row['class_start'], 'class_end':
    row['class_end'], 'duration': duration_rounded}

#return render templates and pass arguments
  return render_template('main.html', main=main, last=last_day,
  following=following_month, first=first_weekday, previous=previous_month,
  daysWithClasses=daysWithClasses, classes=classes, total=total_hours, user=userDetails,
  earned=earned)


# Route for displaying the details of a day
@app.route('/<int:year>/<int:month>/<int:day>')
def day(year, month, day):

  # Checking if user's logged in, if not redirect to login page
  if not user:
    return redirect(url_for('login'))

  sql = "SELECT * FROM classes WHERE year=? AND month=? AND day=? AND user=?"
  event = queryDatabase(sql, [year, month, day, user], one=True)
  formatTime = '%H:%M'
  if event:
    duration = datetime.strptime(event['class_end'], formatTime) - datetime.strptime(event['class_start'], formatTime)
    duration_rounded = duration.total_seconds() / 3600.0
    sql = "SELECT * FROM users WHERE user=?"
    row = queryDatabase(sql, [user], one=True)
    earned = row['pay'] * duration_rounded
  else:
    duration_rounded = None
    earned = None
  return render_template('classInput.html', year=year, month=month, day=day,
  event=event, duration=duration_rounded, earned=earned)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

