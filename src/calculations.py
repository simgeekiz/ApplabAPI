import pandas as pd
import math
import datetime


def calculate_scores(data):
    """Calculates the abilities scores

    .. todo:: Call this function in :func:`app.insert` function
    """
    # calculate the scores
    # add the scores to data
    # Return the enriched data

    def getResponseTime(data):
        """Computes the response times for every answer except the first and last of the day"""
        data.sort_values(by="SubmitDateTime")
        all_dates_times = [datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f') for i in data["SubmitDateTime"]]
        unique_dates = set([dstrftime(d, '%Y-%m-%d') for d in all_dates_times])
        RT = []
        D = []
        D.append(0)
        for u in range(1, len(unique_dates)):
            D.append((datetime.datetime.strptime(unique_dates[u - 1], '%Y-%m-%d') - datetime.datetime.strptime(unique_dates[u], '%Y-%m-%d')).days)


        for u in unique_dates:
            daily_data = data.loc[data["SubmitDateTime"].isin(u)]
            times = [dstrftime(i, '%H:%M:%S.%f') for i in [datetime.datetime.strptime(dd, '%Y-%m-%d %H:%M:%S.%f') for dd in daily_data["SubmitDateTime"]]
            responseTimes = [times[i - 1] - times[i] for i in range(1, len(times))]
            print(responseTimes)
            RT.append(responseTimes)

        return RT, D

    def getExerciseAnswer(data):
        # TODO develop this method
        return data["Correct"]

    def computeUncertainty(D, U):
        """
        Equation (5) in Klinkerberg's paper
        """
        U = U - 1/40 + 1/30 * D
        return U

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

    def computeHSHSscore(x_ij, d_i, t_ij):
        """
        Equation (6) in Klinkerberg's paper
        High Speed High Stakes

        x_ij : bool, answer correct or incorrect to item ij
        t_ij : float, response time for item ij
        d_i : float, time limit
        a_i : float, disctimination parameter = 1 / d_i
        """
        a_i = 1 / d_i
        S_ij = (2 * x_ij - 1) * (a_i * d_i - a_i * t_ij)

    def getExpectedScore(d_i, theta_j, beta_i):
        """
        Equation (7) in Klinkerberg's paper
        """
        a_i = 1 / d_i

        Es_ij = a_i * d_i * ((math.exp(2 * a_i * d_i * (theta_j - beta_i)) + 1)
                             / math.exp(2 * a_i * d_i * (theta_j - beta_i)) - 1)
                             - (1 / (theta_j - beta_i))
         return Es_ij

     def computeERS(theta_j, beta_i, K, S_ij, Es_ij):
         """
         Equation (3) in Klinkerberg's paper
         theta = ability estimate for user
         beta = difficulty estimate for item
         """
         theta = theta_j + K * (S_ij - Es_ij)
         beta = beta_i + K * (Es_ij - S_ij)
         return theta, beta


    userID = data['UserId']
    # FIXME t_i: separate response times by day and match them with exercises (i.e. exclude first and last of the day)
    t_j, D = getResponseTime(data)

    x_j = getExerciseAnswer(data)
    U = 0
    K = 0
    d_i = 0 # TODO find out how this value is decided
    theta_j = 0
    beta_i = 0
    Es_ij = 0
    for it in len(t_i):
        U = computeUncertainty(D, U)
        S_j = computeHSHSscore(x_j[it], d_i[it], t_j[it])
        K = computeDevFromExp(K, U)
        theta_j, beta_i = computeERS(theta_j, beta_i, K, S_ij, Es_ij)
        Es_ij = getExpectedScore(d_i[it], theta_j, beta_i)

    # TODO return dataframe that includes Es_ij and beta_i in the correct positions 
    return data
