import pandas as pd
import math
import datetime

def getResponseTime(data):
    """Computes the response times for every answer except the first and last of the day"""  
    data = pd.DataFrame(data)
    data['SubmitDateTime'] = pd.to_datetime(data['SubmitDateTime'])
    data = data.sort_values(by="SubmitDateTime").reset_index(drop=True)
    unique_dates = sorted(list({date_time_obj.date() for date_time_obj in data['SubmitDateTime']}))
    daily_df_list = []
    for udate in unique_dates:
        daily_data = data.loc[data["SubmitDateTime"].dt.date == udate]
        daily_data = daily_data.reset_index(drop=True)
        response_times = []
        for i, row in daily_data.iterrows():
            if i == 0:
                response_times.append(None)
            else:
                response_times.append((row["SubmitDateTime"] - daily_data["SubmitDateTime"][i-1]).total_seconds())
        daily_data['ResponseTime'] = response_times
        daily_df_list.append(daily_data)
    enriched_df = pd.concat(daily_df_list).reset_index(drop=True)
    enriched_json = enriched_df.to_dict(orient='records')
    return enriched_json

def calculate_scores(data):
    """Calculates the abilities scores

    .. todo:: Call this function in :func:`app.insert` function
    """
    # calculate the scores
    # add the scores to data
    # Return the enriched datas

    def getU(D,U):
        U = U - (1/40) + ((1/30) * D)
        if U <= 0:
            return 0
        return U

    def computeHSHSscore(x_ij, d_i, t_ij):
        """
        Equation (6) in Klinkerberg's paper
        High Speed High Stakes

        x_ij : bool, answer correct or incorrect to item ij
        t_ij : float, response time for item ij
        d_i : float, time limit
        a_i : float, disctimination parameter = 1 / d_i
        """
        if t_ij == None:
            return None

        a_i = 1 / d_i
    #    try:
    #        t = (datetime.datetime.strptime(t_ij, '%H:%M:%S.%f'))#.timestamp()
    #    except:
    #        t = (datetime.datetime.strptime(t_ij, '%H:%M:%S'))#.timestamp()
    #    t = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
    #    t_ij = t.total_seconds()

        S_ij = (2 * x_ij - 1) * (a_i * d_i - a_i * t_ij)
        return S_ij

    def computeDevFromExp(K, U):
        """
        Equation (4) in Klinkerberg's paper
        K measures the ability score changes over the exercises
        """
        if U == 0:
            # K has default value when there is no uncertainty
            return 0.0075
        K_p = 4
        K_m = .5

        return K * (1 + K_p * U - K_m * U)


    def computeERS(theta_j, beta_i, K, S_ij, Es_ij):
        """
        Equation (3) in Klinkerberg's paper
        theta = ability estimate for user
        beta = difficulty estimate for item
        """
        if S_ij == None:
            return theta_j, beta_i
        theta = theta_j + K * (S_ij - Es_ij)
        beta = beta_i + K * (Es_ij - S_ij)
        return theta, beta

    def getExpectedScore(d_i, theta_j, beta_i):
        """
        Equation (7) in Klinkerberg's paper
        """
        a_i = 1 / d_i

        div1 = (math.exp(2 * a_i * d_i * (theta_j - beta_i)) + 1)
        div2 = math.exp(2 * a_i * d_i * (theta_j - beta_i))
        #print(div1, div2)
        #print(theta_j, beta_i)
        Es_ij = a_i * d_i * (div1/ div2 - 1)- (1 / (theta_j - beta_i))
        return Es_ij

    def getExerciseAnswer(data):
        # TODO develop this method Right now not in use
        return data["Correct"]

    data = pd.DataFrame(data)
    data['SubmitDateTime'] = pd.to_datetime(data['SubmitDateTime'])    
    unique_dates = sorted(list({item.date() for item in data['SubmitDateTime']}))
    D = [0] + [(unique_dates[u+1] - unique_dates[u]).days for u in range(0, len(unique_dates) - 1)]
    data['D'] = [D[unique_dates.index(date_time_obj.date())] for date_time_obj in  data["SubmitDateTime"]]
    d_i = [500] * len(data)
    U = 1
    Us = []
    K = 0.01
    Es_ij = 0
    theta_j = 0.00001
    beta_i = 1
    Ks = []
    SSSS = []
    for i, row in data.iterrows():

        U = getU(row['D'], U)

        #print("U:",U, "D:", row['D'], "K:", K)

        S_j = computeHSHSscore(row['Correct'], d_i[i], row['ResponseTime'])

        Us.append(U)

        K = computeDevFromExp(K, U)
        Ks.append(K)

        #theta_j, beta_i = computeERS(theta_j, beta_i, K, S_j, Es_ij)

        Es_ij = getExpectedScore(d_i[i], theta_j, beta_i)

        SSSS.append(Es_ij)
    data['AbilityScore'] = SSSS 
    data_json = data.to_dict(orient='records')
    return data_json
