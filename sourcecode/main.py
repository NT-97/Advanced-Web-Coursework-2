from flask import Flask, render_template
from datetime import date, timedelta
from calendar import monthrange

app = Flask(__name__)

@app.route('/')
@app.route('/<int:year>/<int:month>')
def root(year=None, month=None):

  
  general = date.today()
  
  if year and month:
    general = general.replace(year=year, month=month)

 
  endDay = monthrange(general.year, general.month)[1]
  
  nextMonth = general.replace(day=endDay) + timedelta(days=1)

  firstDayofWeek = monthrange(general.year, general.month)[0]
  
  previousMonth = general.replace(day=1) - timedelta(days=1)
  
  return render_template('main.html', general=general, last=endDay,
  following=nextMonth, first=firstDayofWeek, previous=previousMonth)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
