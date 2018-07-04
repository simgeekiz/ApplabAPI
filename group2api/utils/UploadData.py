### This file is meant to run from pc, *not* from the server. It extracts the
# data from the datafile, posts it to the database and finally runs the day
# command to add the day to the data.
import math

import pandas as pd
import requests

day_of_month = 6


def upload_data(fname):
    data = extract_data(fname)
    data_dict_list = []
    url = create_url()
    for _, row in data.iterrows():
        aaa = row[5]
        if math.isnan(aaa):
            aaa = 'NULL'
        dict = {"SubmitDateTime": str(row[0]),
                "UserId": row[1]+1000,
                "ExerciseId": row[2],
                "LearningObjectiveId": 8025,
                "Correct": min(row[4], 1),
                "AbilityAfterAnswer": aaa}
        data_dict_list.append(dict)
        print(dict, ",")
    # r = requests.post(url=url + "insert/", json=data_dict_list[0],
    #                   auth=("Group2", "Group2-1234"))
    # print(r.status_code, r.reason, url + "insert/")
    r = requests.get(url + "add_days/start=2018-06-04&end=2018-06-0{}".format( str(day_of_month)), auth=("Group2", "Group2-1234"))
    print(r.status_code, r.reason,
          url + "add_days/start=2018-06-04&end=2018-06-0{}".format(
              day_of_month))


def extract_data(fname):
    data = pd.read_excel(fname)
    return data


def create_url():
    url = "http://applab.ai.ru.nl:5000/"
    return url


if __name__ == "__main__":
    day_of_month = 6
    upload_data("C:/Users/Rick "
                "Dijkstra/Documents/Study/Applab/SnappetDataAnoniem/"
                "resultaten-radboud_anoniem 4-6-18.xlsx")
