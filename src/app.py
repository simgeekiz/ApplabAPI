from flask import Flask, request, jsonify#, render_template
app = Flask(__name__)

import json
import pandas as pd

# Custom scripts
import settings as st

@app.route('/')
def hello_world():
    return "It works."
    # return render_template('index.html')

@app.route('/number_of_data')
def get_numbers():
    df = pd.read_csv(st.DATA_PATH)
    return jsonify(number_of_data=len(df))

@app.route('/users')
def get_user_list():
    """Lists the ids of the unique users

    Usage example : http://localhost:5000/users

    Returns
    -------
    users : list of integers
        The list of user's ids
    """
    df = pd.read_csv(st.DATA_PATH)
    user_list = df['UserId'].unique()
    return jsonify(users=user_list.tolist())

@app.route('/user/user_id=<user_id>')
def get_user_info(user_id):
    """Returns the list of activities belongs to a specific user

    Usage example : http://localhost:5000/user/user_id=231412

    Parameters
    ----------
    user_id : integer or string
        Give the id of the user

    Returns
    -------
    user_info : list of dictionaries
        The list of user's activities
    """
    df = pd.read_csv(st.DATA_PATH)
    user_info = df.loc[df['UserId'] == int(user_id)]
    return user_info.to_json(orient='records')

@app.route('/exercises/user_id=<user_id>&learning_obj_id=<learning_obj_id>')
def get_exercises(user_id, learning_obj_id):
    """Returns the list of exercises has been done by the user on a particlar learning objective

    Usage example : http://localhost:5000/scores/user_id=231412&learning_obj_id=554363

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
    df = pd.read_csv(st.DATA_PATH)
    exercises = df[(df['UserId'] == int(user_id)) &
                   (df['LearningObjectiveId'] == int(learning_obj_id))
                  ]['ExerciseId'].unique()
    return jsonify(exercises=exercises.tolist())

@app.route('/scores/user_id=<user_id>&learning_obj_id=<learning_obj_id>&exercise_id=<exercise_id>')
def get_scores(user_id, learning_obj_id, exercise_id):
    """Returns ability score of the user on an exercise for a learning objective

    Usage example : http://localhost:5000/scores/user_id=231412&learning_obj_id=65745&exercise_id=342342

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
    df = pd.read_csv(st.DATA_PATH)
    scores = df[(df['UserId'] == int(user_id)) &
                (df['LearningObjectiveId'] == int(learning_obj_id)) &
                (df['ExerciseId'] == int(exercise_id))
               ]['AbilityAfterAnswer']
    score_list = []
    for score in scores:
        if score in ['NULL ', 'NULL', None]:
            score_list.append(None)
        else:
            score_list.append(int(score))
    return jsonify(scores=score_list)

@app.route('/insert', methods=['POST'])
def insert():
    """Accepts data in JSON format and saves it to the file.

    In order to use it, the data should be *POSTed*.
    Usage example with Python requests library::

        import requests
        data = [{"SubmitDateTime":"2012-12-21 12:12:12.120",
                 "UserId":2464375364,
                 "ExerciseId":141464536,
                 "LearningObjectiveId":11424,
                 "Correct":1,
                 "AbilityAfterAnswer":"14143"}
        requests.post("http://localhost:5000/insert", json=data)
    """
    df = pd.read_csv(st.DATA_PATH)
    data_df = pd.DataFrame(request.get_json())
    df = df.append(data_df, ignore_index=True)
    # TODO: Calculate the scores right here before saving the data back (see calculate_scores())
    df.to_csv(st.DATA_PATH)
    return jsonify(message="Data succesfully inserted and saved.")

if __name__ == '__main__':
	app.run()
