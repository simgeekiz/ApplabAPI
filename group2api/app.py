from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__)

import os
import sys
sys.path.append('..')
from datetime import datetime, timedelta
import json
from pymongo import MongoClient

try:
    from .utils import calculations as calc
except ImportError:
    from utils import calculations as calc

try:
    from .utils import moment as mo
except ImportError:
    from utils import moment as mo

# Connect to mongoLab
client = MongoClient(os.environ['MONGO_HOST'], int(os.environ['MONGO_PORT']))
db = client[os.environ['MONGO_DBNAME']]

# Authentication is only needed for db in mLab servers
# db.authenticate(os.environ['MONGO_DBUSER'], os.environ['MONGO_DBPASS'])

submissions = db['submissions']
users = db['users']
#coordinates = db['coordinates']

@app.route('/check_connection/')
def check():
    return "Hmm"

@app.route('/see_change')
def testing():
    return jsonify(message="This really is working :)")

@app.route('/')
def hello_world():
    """Display the home page

    Usage example : <hostname>/
    """
    return 'For documentation see /docs'


@app.route('/docs')
def serve_docs():
    """Display the documentations

    Usage example : <hostname>/docs
    """
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
    return jsonify(number_of_submissions=submissions.count())


@app.route('/users')
def get_user_list():
    """Lists the ids of the unique users

    Usage example : <hostname>/users

    Returns
    -------
    users : list of integers
        The list of user ids
    """
    user_list = submissions.distinct('UserId')
    return jsonify(user_list)


@app.route('/login_users')
def get_user_login_info():
    """Lists the userids, names and passwords

    Usage example : <hostname>/login_users

    Returns
    -------
    all_login_users : list of dictionaries
        The list of user login information
    """
    loginusers = users.find({}, {'_id': 0})
    all_login_users = [u for u in loginusers]
    return jsonify(all_login_users)


@app.route('/login_users/username=<username>')
def get_user_login_info_with_user(username):
    """Get the user id, name and password based on username

    Usage example : <hostname>/login_users/username=user15379
    
    Parameters
    ----------
    username : string
        Give user name of the user.

    Returns
    -------
    login_user : list
        User login information
    """
    login_user_info = users.find({'UserName': username}, {'_id': 0})
    login_user = [u for u in login_user_info]
    return jsonify(login_user)

@app.route('/get_data/date=<date>')
def get_data_by_date(date):
    """Get the list of data for one specific submission date

    Usage example : <hostname>/get_data/date=2017-11-28
    
    Parameters
    ----------
    date : string
        Give the date string in YYYY-DD-MM format.

    Returns
    -------
    data : list
        Returns list of instances belongs to the date
    """
    data = submissions.find({'SubmitDateTime': {'$regex': '^' + date + '.*'}}, {'_id': 0})
    data = [d for d in data]
    return jsonify(data)

@app.route('/get_data/day=<day_number>')
def get_data_by_day_number(day_number):
    """Get the list of data for one specific submission date

    Usage example : <hostname>/get_data/day=1
    
    Parameters
    ----------
    day_number : int
        Give the date number like 1, 2, 3.

    Returns
    -------
    data : list
        Returns list of instances belongs to one day
    """
    data = submissions.find({'Days': int(day_number)}, {'_id': 0})
    data = [d for d in data]
    return jsonify(data)

@app.route('/scores/day=<day_number>&user_id=<user_id>&learning_obj_id=<learning_obj_id>')
def get_ability_score_by_day_number(day_number, user_id, learning_obj_id):
    """Returns ability score of the user accordind to learning obj id

    Usage example : <hostname>/scores/day=1§user_id=231412&learning_obj_id=65745
    
    Parameters
    ----------
    
    day_number : int 
        Give the date number like 1, 2, 3
        
    user_id : integer or string
        Give the id of the user

    learning_obj_id : integer or string
        Give the id of the learning objective

    Returns
    -------
    scores : an integer
        The ability score achieved by the user
    """
    scores = submissions.find(
        {'Days': int(day_number),
         'UserId': int(user_id),
         'LearningObjectiveId': int(learning_obj_id)},
        {'_id': 0, 'AbilityAfterAnswer': 1, 'SubmitDateTime': 1})
    
    datetime_list = []
    data = [d for d in scores]
    
    for i in data:
        datetime_list.append(datetime.strptime(i['SubmitDateTime'], '%Y-%m-%d %H:%M:%S.%f'))
    index = datetime_list.index(max(datetime_list))
    while (data[index]['AbilityAfterAnswer'] == None):
        datetime_list.pop(index)
        index = datetime_list.index(max(datetime_list))
    return jsonify(data[index]['AbilityAfterAnswer'])


@app.route('/upload_login_users')
def upload_login_users():
    """Generates user information with default values

    Usage example : <hostname>/user_login_info
    """
    submissions_user_ids = submissions.distinct('UserId')
    users_user_ids = users.distinct('UserId')
    user_ids = [uid for uid in submissions_user_ids if
                uid not in users_user_ids]
    for uid in user_ids:
        user_info = {}
        user_info['UserId'] = uid
        user_info['UserName'] = 'user{}'.format(str(uid))
        user_info['Password'] = 1234
        users.insert(user_info)
    return jsonify(message="Users generated")


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
    infos = submissions.find({'UserId': int(user_id)}, {'_id': 0})
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
                                  'LearningObjectiveId': int(
                                      learning_obj_id)}).distinct('ExerciseId')

    exercises_list = []
    for ex in exercises:
        if ex in ['', 'null ', 'null', 'NULL ', 'NULL', None]:
            exercises_list.append(None)
        else:
            exercises_list.append(int(ex))
    return jsonify(exercises_list)


@app.route(
    '/scores/user_id=<user_id>&learning_obj_id=<learning_obj_id>&exercise_id=<exercise_id>')
def get_ability_scores(user_id, learning_obj_id, exercise_id):
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
        {'_id': 0, 'AbilityAfterAnswer': 1})

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

    .. todo:: Run only on the data that doesn't have any response time

    Parameters
    ----------
    user_id : integer or string, (default='all')
        Give the id of the user. If given 'all', runs for
        each unique user in the database.
    """
    user_ids_list = submissions.distinct('UserId') if user_id == 'all' else [
        user_id]
    for user_id in user_ids_list:
        user_subs = submissions.find({'UserId': int(user_id)},
                                     {'_id': 1, 'SubmitDateTime': 1})
        user_subs = [sub for sub in user_subs]
        resp_time_enrich = calc.get_response_time(user_subs)
        for item in resp_time_enrich:
            submissions.update({'_id': item['_id']}, {
                '$set': {'ResponseTime': item['ResponseTime']}})
    return jsonify(message="Response times succesfully added.")


@app.route('/calculate_scores/user_id=<user_id>')
def calculate_scores(user_id='all'):
    """Calculates the ability scores for the given user or for all
    
    .. warning:: If run for all users, it takes a while
    
    Parameters
    ----------
    user_id : integer or string, (default='all')
        Give the id of the user. If given 'all', runs for
        each unique user in the database.
        
    Returns
    -------
    response : dictionary
        Contains a success message and a list of failed user ids.
    """
    response = {
        "message": "Calculated Ability scores succesfully added.",
        "failed_ids": []
    }
    user_ids_list = submissions.distinct('UserId') if user_id == 'all' else [user_id]
    for user_id in user_ids_list:
        user_subs = submissions.find({'UserId': int(user_id)},
                                     {'_id': 1, 'SubmitDateTime': 1,
                                      'ExerciseId': 1, 'ResponseTime': 1,
                                      'Correct': 1})
        user_subs = [sub for sub in user_subs]
        try:
            calculated_ability_score = calc.calculate_scores(user_subs)
        except KeyError:
            response['failed_ids'].append(user_id)
        else:
            for item in calculated_ability_score:
                submissions.update({'_id':item['_id']}, {'$set': {'AbilityScore': item['AbilityScore']}})
    return jsonify(response)

@app.route('/add_days/start=<start_date>&end=<end_date>')
def add_days(start_date, end_date):
    """Adds the days information to the instances based on given interval

    Usage example : <hostname>/add_days/start=2017-11-28&end=2017-12-04
    
    Parameters
    ----------
    start_date : string
        Give the starting date as string in YYYY-DD-MM format.
        
    end_date : string
        Give the ending date as string in YYYY-DD-MM format.
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    date_list = [((start_date + timedelta(n)).strftime('%Y-%m-%d'), n+1)
                 for n in range(int((end_date - start_date).days)+1)]
    
    submissions.update({}, {'$unset': {'Days': 1}}, multi=True)

    for date, days in date_list:
        submissions.update({'SubmitDateTime': {'$regex': '^' + date + '.*'}}, 
                           {'$set': {'Days': days}}, 
                           multi=True)
    
    return jsonify(message="Days added.")


@app.route('/insert', methods=['POST'])
def insert():
    """Accepts data in JSON format and saves it to the file.

    In order to use it, the data should be *POSTed*.
    Data should consist of list of dictionaries.
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
    
    try:
        response_time_enrichment(user_id='all')
    except:
        return jsonify(error="Error during response time enrichment")
    
   # try:
  #      calculate_scores(user_id='all')
  #  except: 
   #     return jsonify(error="Error during calculate scores")
    
    try:
        upload_login_users()
    except: 
        return jsonify(error="Error during uploading users to database")
        
    return jsonify(message="Data succesfully inserted and saved.")


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    """Checks if the requested used_id is present in the submission list,
    and if the password matches the one set by the user.
    """
    import pandas as pd
    # received = request.data.decode('utf-8')
    # TODO delete this when post request works
    received = '874250:1234'
    user_id, password = received.split(':')
    usr = "user" + user_id

    data_pd = pd.DataFrame(list(users.find()))
    
    try:
        with open('received.txt', 'w') as f:
            f.write(received)
            
        unames = data_pd['UserName'].tolist()
        if user_id == None or usr not in unames:
            return "Wrong username"

        elif usr in unames:
            ind = unames.index(usr)
            if password == str(data_pd["Password"][ind]):
                return "Correct"
            else:
                return "Wrong password"
    except:
        with open('received.txt', 'a') as f:
            f.write("failed")
        return "Error"

@app.route('/calculate_m2m_coordinates/user_id=<user_id>')
@app.route('/calculate_m2m_coordinates/user_id=<user_id>/date=<date>')
def calculate_m2m_coordinates(user_id, date=None):
    """Calculates coordinates that represent the learning of the moment-by-moment peaks.
    
    Parameters
    ----------
    user_id : The user for which the coordinates are calculated
    
    date : string, optional (default=None)
        pass in yyyy-mm-dd format. Will result in getting just the coordinates for that day
    
    Returns
    -------
    coords : The coordinates for which the
    """
    submissiondata = submissions.find({}, {'_id': 0})
    sub = [u for u in submissiondata]
    handler = mo.DataHandler(sub)
    if date is None:
        coords = handler.get_coordinates_for_today(int(user_id))
    else:
        date = mo.get_date_from_str(date)
        coords = handler.get_coordinates_for_today(int(user_id), date_id=date)
    return json.dumps(coords, cls=mo.MyEncoder)

if __name__ == '__main__':
    app.run()
