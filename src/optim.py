import cvxpy as cvx
import numpy as np


def solve(n_p, n_d, n_s, gender, teach, matur, indisp, hist=None):
    """ Solves the Integer Programming problem that generates a schedule.
    The current constraints are, maximum of one man per slot...

    n_p is the number of people
    n_d is the number of days
    n_s is the number of slots per day
    gender is a np array of 1 and 0
    teach
    matur
    indisp is a list of tuples corresponding to the the date indisponibilities
    """
    # TODO Change the disp matrix to slots? Maybe add another constraint 
    # source, specifically targeting the day and slot. 
    # To fix someone on a specific role you can set the other slots to 0
    # every day.

    X = cvx.Bool(n_p,n_d*n_s)

    # Date Indisponibility constraints
    ind_constr = []
    for tup in indisp:
        ind_constr.append([X[tup[0], tup[1]*n_s + k] == 0 for k in range(n_s)])
    print(ind_constr)
    


if __name__ == "__main__":
    n_p_ = 8
    n_d_ = 2
    n_s_ = 2
    # G = np.asarray([])
    indisp = [(1,1), (2,0), (5,0)]
    solve(n_p_, n_d_, n_s_,0,0,0,indisp)

