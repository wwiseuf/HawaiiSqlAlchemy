import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

import os


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


# create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """
    
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/prcp<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/prcp")
def prcp():

    print("Received prcp api request.")
    
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    
    begin_date = max_date - dt.timedelta(365)
    
    precipitation_data = session.query(func.strftime("%Y-%m-%d", measurement.date), measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", measurement.date) >= begin_date).all()

# results dictionary
    resulting = {}
    for result in precipitation_data:
        resulting[result[0]] = result[1]
        
    return jsonify(resulting)

    #Return a list of all passenger names"""
    # Query stations

    @app.route("/api/v1.0/station")
    def station():
        """Return a JSON list of stations from the dataset."""

    print("Received station api request.")

    #query stations list
    stations = session.query(station).all()

    #create a list of dictionaries
    stationlist = []
    for station in stations:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stationlist.append(stationlist)

    return jsonify(stationlist)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""

    print("Received tobs api request.")

    #We find temperature data for the last year.  First we find the last date in the database
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    #set beginning of search query
    begin_date = max_date - dt.timedelta(365)

    #get temperature measurements for last year
    results = session.query(measurement).\
        filter(func.strftime("%Y-%m-%d", measurement.date) >= begin_date).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_tobs = []
    for result in results:
        
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)