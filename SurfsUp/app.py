# Import the dependencies.
import sqlalchemy
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func, text, inspect
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data"""
    # Starting from the most recent data point in the database. 
    recent_date = dt.date(2017, 8, 23)
    # Calculate the date one year from the last date in data set.
    year_ago = recent_date - relativedelta(years=1)
    # Perform a query to retrieve the date and precipitation scores fot the last 12 months of data
    prcp_data = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= year_ago).all()
    # Convert the query result to a dictionary
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    # Return the dictionary as JSON
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations""" 
    # Perform a query to retrieve the station names in the datataset
    station_list = session.query(station.name).all()
    # Convert list of tuples into normal list
    list_result = list(np.ravel(station_list))
    return jsonify(list_result)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of date and temperature for the most active station for the previous year"""
    # Starting from the most recent data point in the database. 
    recent_date = dt.date(2017, 8, 23)
    # Calculate the date one year from the last date in data set.
    year_ago = recent_date - relativedelta(years=1)
    # Query date and temperature for the most active station for the previous year
    temp_data = session.query(measurement.tobs).\
    filter(measurement.date >= year_ago).\
    filter(measurement.station == 'USC00519281').\
    all()
    # Convert list of tuples into normal list
    list_result2 = list(np.ravel(temp_data))
    return jsonify(list_result2)

@app.route('/api/v1.0/<start>')
def get_temperatures_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature from a specified start date"""
    result = calculate_temperatures(start)
    return jsonify(result)

@app.route('/api/v1.0/<start>/<end>')
def get_temperatures_range(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature from a specified start-end range"""
    result = calculate_temperatures(start, end)
    return jsonify(result)

def calculate_temperatures(start_date, end_date=None):
    # Calculate the lowest, highest, and average temperature for the specified dates.
    if end_date:
        temperatures = session.query(func.min(measurement.tobs).label('min_temp'),
                                     func.avg(measurement.tobs).label('avg_temp'),
                                     func.max(measurement.tobs).label('max_temp')) \
            .filter(measurement.date >= start_date, measurement.date <= end_date) \
            .first()
    else:
        temperatures = session.query(func.min(measurement.tobs).label('min_temp'),
                                     func.avg(measurement.tobs).label('avg_temp'),
                                     func.max(measurement.tobs).label('max_temp')) \
            .filter(measurement.date >= start_date) \
            .first()

    # Convert result to dictionary
    result_dict = {
        'min_temperature': temperatures.min_temp,
        'avg_temperature': temperatures.avg_temp,
        'max_temperature': temperatures.max_temp
    }

    return result_dict

# Close Session
session.close()

if __name__ == '__main__':
    app.run(debug=True)