# Import the dependencies.

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine 
from sqlalchemy import func 
from datetime import datetime as dt
from flask import Flask,jsonify



#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


# Create our session (link) from Python to the DB
session = Session(engine)

#last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first() 
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route('/')
def welomce():
    '''List all available api routes.'''
    return(
        f'Welcome to the Weather Station API<br>'
        
        f'Available Routes:<br/>'
        f'Precipitation from last year of data:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'List of stations:<br/>'
        f'/api/v1.0/stations<br/>'
        f'Temperature readings of busiest station over last year:<br/>'
        f'/api/v1.0/tobs<br/>'
        f'Min, Max, and Average temps for given start date:<br/>'
        f'/api/v1.0/start<br/>'
        f'Min, Max, and Average temps for given date range:<br/>'
        f'/api/v1.0/start/end'
    )
@app.route('/api/v1.0/precipitation')

def precip():
    session = Session(engine)
    #Query to find prcp data from last year
    sel=[Measurement.date,Measurement.prcp]
    results= session.query(*sel).\
        filter(Measurement.date >='2016-08-23').\
            order_by(Measurement.date).all()

    session.close() 
    #Turn data into a dictionary       
    last_year_data= {key:value for (key,value) in results}
    last_year_data = jsonify(last_year_data)
    return(last_year_data)
 

 
@app.route('/api/v1.0/stations')   

def stations():
  session = Session(engine)
  #Query for all stations and return as json
  total_stations =  session.query(Station.station).all()
  session.close()
  station_list = list(np.ravel(total_stations))
  return(jsonify(station_list))

@app.route('/api/v1.0/tobs')

def tobs():
    #Query for busiest station data over last year
    session = Session(engine)
    most_active = session.query(Measurement.station,func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).first()
    busiest_station_data = session.query(Measurement.station,Measurement.date,Measurement.tobs).\
    filter(Measurement.station== most_active[0]).\
    filter(Measurement.date >= '2016-08-16')

            

        
    session.close()

    #Adding data to dictionary and turning into json
    most_active_data = []
    for station, date, tobs in busiest_station_data:
        busiest_station = {}
        busiest_station['station']= station
        busiest_station['date']= date
        busiest_station['tobs'] = tobs
        most_active_data.append(busiest_station)
 
    return  jsonify(most_active_data)

    
 
 
@app.route('/api/v1.0/start/<start>')   

def from_start_date(start):
    session = Session(engine)
    temps = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()
    temps_results = []
    temps_dict = {
        'Begin From': start,
        'Min': temps[0][0],
        'Max': temps[0][1],
        'Mean':temps[0][2]
    }

    temps_results.append(temps_dict)

    return(jsonify(temps_results))

@app.route('/api/v1.0/start/end/<start>/<end>')

def start_end(start,end):
    session = Session(engine)
    temps_start_end = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <=end).all()
    session.close()
    temps_range = []
    temps_range_dict = {
        'Begin From': start,
        'End On': end,
        'Min': temps_start_end[0][0],
        'Max': temps_start_end[0][1],
        'Mean':temps_start_end[0][2]
    }

    temps_range.append(temps_range_dict)

    return(jsonify(temps_range))

  
  
      

   
    


    


if __name__ == "__main__":
    app.run(debug=True)
