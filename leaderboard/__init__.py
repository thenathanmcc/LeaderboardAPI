from datetime import timedelta
from flask import Flask, url_for, request, redirect, jsonify, abort
from flask_cors import CORS, cross_origin

import hvac
import psycopg2
from psycopg2 import Error
from werkzeug.wrappers import response

app = Flask(__name__, instance_relative_config = True)
CORS(app, support_credentials = True)
app.config["DEBUG"] = True


# PostgreSQL database connection parameters
DATABASE_USER = "test"
DATABASE_USER_PASSWORD = "test_password"
DATABASE_HOST = "127.0.0.1"
DATABASE_PORT = "5432"
DATABASE_NAME = "test_database"

@app.route('/api/v1/scoreboard', methods=['GET'])
@cross_origin(supports_credentials=True)
def ranking():
    """
    Retrieves the current scoreboard from the PostgreSQL database sorted by fastest race time.

    GET request arguments should contain the specified race track. If none is sent in the request, the default used is
    the Low Earth Orbit track.
    """
    # Get race track string from request arguments
    race_track = request.args.get("race_track")
    # If no value specified, use default.
    if not race_track:
        race_track = "Low Earth Orbit"

    try:
        connection = psycopg2.connect(user=DATABASE_USER, password=DATABASE_USER_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME)

        cursor = connection.cursor()
        cursor.execute("SELECT player_name, platform, race_track, rocket_type, time_duration FROM scoreboard WHERE race_track = '%s' ORDER BY time_duration ASC;" % race_track)

        # Get column names for json keys
        column_headers = []
        for column in cursor.description:
            column_headers.append(column[0])

        # Build results array
        results = []
        for tuple in cursor.fetchall():
            row = {}
            for i in range(len(tuple)):
                row[column_headers[i]] = str(tuple[i])
            results.append(row)

        return(jsonify({"rows": results}))

    except(Exception, Error) as error:
        return http_response("*** ERROR RETRIEVING SCOREBOARD ***\n" + str(error), status_code=400)
    finally:
        if (connection):
            cursor.close()
            connection.close()

@app.route('/api/v1/add_entry', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_to_scoreboard():
    """
    Adds a new entry to the scoreboard. The POST request must contain all the details needed to add a new row to the 
    scoreboard in the database.

    Data needed:

    player_name : the name of the player
    platform : platform game is running on
    race_track : race track the time was recorded
    rocket_type : the rocket that was used
    time_duration : the time it took to complete the track

    If the POST request doesn't contain all the information, a 400 HTTP status code is returned.

    """
    player_name = request.form.get("player_name")
    platform = request.form.get("platform")
    race_track = request.form.get("race_track")
    rocket_type = request.form.get("rocket_type")
    time_duration = request.form.get("time_duration")

    if not player_name or not platform or not race_track or not rocket_type or not time_duration:
        return http_response("Insufficient Information In Request", status_code=400)

    try:
        connection = psycopg2.connect(user=DATABASE_USER, password=DATABASE_USER_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME)

        cursor = connection.cursor()

        cursor.execute("INSERT INTO scoreboard (player_name, platform, race_track, rocket_type, time_duration) \
            VALUES ('%s', '%s', '%s', '%s', '%s')" % (player_name, platform, race_track, rocket_type, time_duration))
        
        connection.commit()

        return http_response('Scoreboard Updated Successfully', status_code=201) 
    
    except(Exception, Error) as error:
        return http_response("*** ERROR ADDING RECORD ***\n" + str(error), status_code=400)
    finally:
        if (connection):
            cursor.close()
            connection.close()

@app.route('/api/v1/delete_entry', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def delete_from_scoreboard():
    """
    Deletes a row from the scoreboard. DELETE request must contain an id for the row
    """

    row_id = request.args.get("id")

    if not row_id:
        return http_response("Insufficient Information", status_code=400)

    try:

        connection = psycopg2.connect(user=DATABASE_USER, password=DATABASE_USER_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME)

        cursor = connection.cursor()

        cursor.execute("DELETE FROM scoreboard WHERE player_id=%s" % row_id)
        connection.commit()

        return http_response("Entry Deleted Successfully", status_code=200)

    except (Exception, Error) as error:
        return http_response("*** ERROR REMOVING RECORD ***\n" + str(error), status_code=400)
    finally:
        if (connection):
            cursor.close()
            connection.close()


def http_response(message, status_code):
    """
    Create http response with a special message and status_code

    message -- Message to be sent to the client
    status_code -- HTTP status code
    """
    response = jsonify({'message' : message})
    response.status_code = status_code
    return response


app.run()