from flask import Flask, request, jsonify, render_template, send_from_directory
app = Flask(__name__)

import os
import sys
sys.path.append('..')
import json
from pymongo import MongoClient

try:
    from .utils import calculations as calc
except ImportError:
    from utils import calculations as calc

# Connect to mongoLab
client = MongoClient(os.environ['MONGO_HOST'], int(os.environ['MONGO_PORT']))
db = client[os.environ['MONGO_DBNAME']]
db.authenticate(os.environ['MONGO_DBUSER'], os.environ['MONGO_DBPASS'])

submissions = db['submissions']

@app.route('/')
def hello_world():
    return 'For documentation see /docs'

@app.route('/docs')
def serve_docs():
    return render_template('index.html')

@app.route('/number_of_submissions')
def get_number_of_submissions():
    """Gives the total number of submissions

    Usage example : <hostname>/number_of_submissions

    Returns
    -------
    number_of_submissions : list of integers
        The list of user's ids
    """
    return jsonify(number_of_instances=submissions.count())

@app.route('/users')
def get_user_list():
    """Lists the ids of the unique users

    Usage example : <hostname>/users

    Returns
    -------
    users : list of integers
        The list of user's ids
    """
    users = submissions.distinct('UserId')
    return jsonify(users)

@app.route('/user/user_id=<user_id>')
def get_user_info(user_id):
    """Returns the list of activities belongs to a specific user

    Usage example : <hostname>/user/user_id=231412

    Parameters
    ----------
    user_id : integer or string
        Give the id of the user

    Returns
    -------
    user_info : list of dictionaries
        The list of user's activities
    """
    infos = submissions.find({'UserId': int(user_id)}, {'_id':0})
    users_info = []
    for info in infos:
        users_info.append(info)
    return jsonify(users_info)


@app.route('/exercises/user_id=<user_id>&learning_obj_id=<learning_obj_id>')
def get_exercises(user_id, learning_obj_id):
    """Returns the list of exercises has been done by the user on a particlar learning objective

    Usage example : <hostname>/exercises/user_id=231412&learning_obj_id=554363

    Parameters
    ----------
    user_id : integer or string
        Give the id of the user

    learning_obj_id : integer or string
        Give the id of the learning objective

    Returns
    -------
    exercises : list of integers
        The list of unique exercise ids has been done by the user
    """
    exercises = submissions.find({'UserId': int(user_id),
                      'LearningObjectiveId': int(learning_obj_id)}).distinct('ExerciseId')

    exercises_list = []
    for ex in exercises:
        if ex in ['', 'null ', 'null', 'NULL ', 'NULL', None]:
            exercises_list.append(None)
        else:
            exercises_list.append(int(ex))
    return jsonify(exercises_list)

@app.route('/scores/user_id=<user_id>&learning_obj_id=<learning_obj_id>&exercise_id=<exercise_id>')
def get_scores(user_id, learning_obj_id, exercise_id):
    """Returns ability score of the user on an exercise for a learning objective

    Usage example : <hostname>/scores/user_id=231412&learning_obj_id=65745&exercise_id=342342

    Parameters
    ----------
    user_id : integer or string
        Give the id of the user

    learning_obj_id : integer or string
        Give the id of the learning objective

    exercise_id : integer or string
        Give the id of the exercise

    Returns
    -------
    scores : list of integers
        The list of the ability scores achieved by the user
    """
    scores = submissions.find(
        {'UserId': int(user_id),
         'LearningObjectiveId': int(learning_obj_id),
         'ExerciseId': int(exercise_id)},
        {'_id':0, 'AbilityAfterAnswer':1})

    scores_list = []
    for item in scores:
        score = item['AbilityAfterAnswer']
        if score in ['', 'null ', 'null', 'NULL ', 'NULL', None]:
            scores_list.append(None)
        else:
            scores_list.append(int(score))

    return jsonify(scores_list)

@app.route('/response_time_enrichment/user_id=<user_id>')
def response_time_enrichment(user_id='all'):
    """Calculates and adds the response time for each submission

    .. todo:: Only get the data that doesn't have any response time

    Parameters
    ----------
    user_id : integer or string, (default='all')
        Give the id of the user. If given 'all', runs for
        each unique user in the database.
    """
    user_ids_list = submissions.distinct('UserId') if user_id == 'all' else [user_id]
    for user_id in user_ids_list:
        user_subs = submissions.find({'UserId': int(user_id)}, {'_id':1, 'SubmitDateTime':1})
        user_subs = [sub for sub in user_subs]
        resp_time_enrich = calc.get_response_time(user_subs)
        for item in resp_time_enrich:
            submissions.update({'_id':item['_id']}, {'$set': {'ResponseTime':item['ResponseTime']}})
    return jsonify(message="Response times succesfully added.")

@app.route('/calculate_scores/user_id=<user_id>')
def calculate_scores(user_id='all'):

    user_ids_list = submissions.distinct('UserId') if user_id == 'all' else [user_id]
    for user_id in user_ids_list:
        user_subs = submissions.find({'UserId': int(user_id)}, {'_id':1, 'SubmitDateTime':1, 'ExerciseId':1, 'ResponseTime':1, 'Correct':1})
        user_subs = [sub for sub in user_subs]
        calculated_ability_score = calc.calculate_scores(user_subs)
        for item in calculated_ability_score:
            submissions.update({'_id':item['_id']}, {'$set': {'AbilityScore':item['AbilityScore']}})

    return jsonify(message="Calculated Ability scores succesfully added.")

@app.route('/insert', methods=['POST'])
def insert():
    """Accepts data in JSON format and saves it to the file.

    In order to use it, the data should be *POSTed*.
    Data should be consist of list of dictionaries.
    Usage example with Python requests library::

        import requests
        data = [{"SubmitDateTime":"2012-12-21 12:12:12.120",
                 "UserId":2464375364,
                 "ExerciseId":141464536,
                 "LearningObjectiveId":11424,
                 "Correct":1,
                 "AbilityAfterAnswer":14143}]
        requests.post("<hostname>/insert", json=data)
    """
    data_ = request.get_json()
    if type(data_) is not list:
        return jsonify(error="Data should be a list format.")
    try:
        for item in data_:
            submissions.insert(item)
    except:
        return jsonify(error="Error during insertion to database")
    response_time_enrichment(user_id='all')
    calculate_scores(user_id='all')
    return jsonify(message="Data succesfully inserted and saved.")

@app.route('/see_change')
def testing():
    return jsonify(message="this is working :)")

if __name__ == '__main__':
    app.run(debug=True)
