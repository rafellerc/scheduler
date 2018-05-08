import cvxpy as cvx
import numpy as np
from random import randint
import src.tests as tt


def solve(n_p, n_d, n_s, G, T, M, indisp, forced, slot_choice, demand, prop=0.5, hist=None):
    """ Solves the Integer Programming problem that generates a schedule.
    The current constraints are, maximum of one man per slot...

    Args:
        n_p (int): the number of people in the list
        n_d (int): the number of days being considered
        n_s (int): the number of slots of work per day
        G (ndarray): A np array (colum vector) of 1s and 0s representing
        the gender of each person in the list, 1 for man and 0 for woman 
        T (ndarray): A np array (colum vector) representing the teacher
        status of each person in the list, 1 for teacher and 0 for auxiliar 
        M (ndarray): A np array (colum vector) representing the maturity
        status of each person in the list, 1 for mature and 0 otherwise 
        indisp (list): List of tuples corresponding to the the date 
        indisponibilities in the form (person, day)
        forced (list): Similarly to indisp, this list contains the tuples
        of people that we want to force to be present in a given slot in the
        solution. In this case the tuples are (person, day*n_s+slot).
        slot_choice (ndarray): A somewhat dense matrix of shape (n_p, n_s)
        representing the disponibility of each person to work on each slot.
        1 means available, 0 otherwise
        demand (ndarray): A (n_d*n_s) column vector of the demand of people
        for each slot.
        prop (float): Maximum proportion of men in each slot

    Returns:
        solution (ndarray): A matrix of shape (n_p, n_d*n_s) where xij = 1
        represents a person p working on day j//n_s on slot j%n_s 
    """
    # TODO Change the disp matrix to slots? Maybe add another constraint 
    # source, specifically targeting the day and slot. 
    # To fix someone on a specific role you can set the other slots to 0
    # every day.

    X = cvx.Bool(n_p,n_d*n_s)

    demand_constr = []
    for s in range(n_d*n_s):
        demand_constr.append(cvx.sum_entries(X[:, s]) == demand[s])

    # Date Indisponibility constraints
    ind_constr = []
    for p, d in indisp:
        # Check if the list is being correctly appended: The elements, not the list
        ind_constr = ind_constr + [X[p, d*n_s + k] == 0 for k in range(n_s)]
    
    # Gender constraints
    gend_constr = []
    for s in range(n_d*n_s):
        if demand[s] > 1:
            gend_constr.append(G.reshape(1,n_p)*X[:,s] <= prop*demand[s])

    # Teacher constraints
    teach_constr = []
    for s in range(n_d*n_s):
        if demand[s] > 1:
            teach_constr.append(T.reshape(1,n_p)*X[:,s] == 1)
    
    # Maturity constraints
    matur_constr = []
    for s in range(n_d*n_s):
        if demand[s] > 1:
            matur_constr.append(M.reshape(1,n_p)*X[:,s] >= 1)

    # No Repeat constraints
    no_rep_constr = []
    for d in range(n_d):
        for p in range(n_p):
            no_rep_constr.append(cvx.sum_entries(X[p, d*n_s:n_s*(d+1)]) <= 1)

    # Slot (Activity) choice constraint
    slot_constr = []
    for p in range(n_p):
        for s in range(n_s):
            slot_constr = slot_constr + [X[p, s + n_s_*d] <= slot_choice[p, s] for d in range(n_d_)]

    # Forced constraint
    force_constr = []
    for p, d in forced:
        force_constr.append(X[p,d] == 1)

    constraints = (demand_constr 
                  + ind_constr
                  + gend_constr 
                  + teach_constr
                  + matur_constr
                  + no_rep_constr
                  + slot_constr
                  + force_constr
                  )

    # Objective Function
    obj = cvx.Minimize(cvx.max_entries(cvx.sum_entries(X, axis=1)))

    prob = cvx.Problem(obj, constraints)
    prob.solve(solver=cvx.GLPK_MI)
    sol = X.value
    value = prob.value
    if sol is not None:
        # Gets rids of the residues, rounds everything to zero or one
        sol = np.int8(sol.round(2))
        value = int(round(value))

    return prob.status, sol, value

if __name__ == "__main__":
    n_p_ = 64
    n_d_ = 2
    n_s_ = 6
    demand_ = np.asarray([4, 3, 1, 2, 3, 1, 4, 3, 1, 2, 3, 1], dtype=np.int8)
    indisp_ = []
    for k in range(4):
        p_ = randint(0, n_p_-1)
        d_ = randint(0, n_d_-1)
        indisp_.append((p_,d_))
    force_ = []
    for k in range(3):
        p_ = randint(0,3)
        s_ = randint(0,3)
        add = True
        for i in range(len(indisp_)):
            if p_ == indisp_[i][0] and s_//n_s_ == indisp_[i][1]:
                add = False
        if add:
            force_.append((p_,s_))

    G_ = np.random.choice([0, 1], size=([n_p_]), p=[0.7, 0.3])
    prop = 0.5
    T_ = np.int8(np.random.choice([0, 1], size=([n_p_]), p=[0.7, 0.3]))
    M_ = np.int8(np.random.choice([0, 1], size=([n_p_]), p=[0.6, 0.4]))
    slot_choice_ = np.int8(np.random.choice([0, 1], size=([n_p_,n_s_]), p=[0.2, 0.8]))


    status, sol_, max_workload = solve(n_p_, n_d_, n_s_,
                                G_, T_, M_, indisp_, force_, slot_choice_, demand_, prop)

    print("Status: ", status, "| Max workload: ", max_workload)
    print("Solution: \n", sol_)

    # Tests
    if sol_ is None:
        print("The given instance is INFEASIBLE. Try relaxing some of the constraints")
    else:
        # Demand Test
        dem_test, dem_fail = tt.test_demand(n_p_,n_d_,n_s_, sol_, demand_)
        if dem_test and status=='optimal':
            print('Demand test SUCCESS')
        else:
            print('Demand test failed. Error instances: ', dem_fail)

        # Indisponibility Test
        ind_test = tt.test_indisp(n_p_,n_d_,n_s_, sol_, indisp_)
        if dem_test and status=='optimal':
            print('Indisponibility test SUCCESS.')
        else:
            print('Indisponibility test FAILED.')
        
        # Gender Test
        gen_test, gen_fail = tt.test_gender(n_p_,n_d_,n_s_, sol_, G_, demand_, prop)
        if gen_test and status=='optimal':
            print('Gender test SUCCESS.')
        else:
            print('Gender test FAILED. Failed instances: ', gen_fail)

        # Teacher Test
        teach_test, teach_fail = tt.test_teacher(n_p_,n_d_,n_s_, sol_, T_, demand_)
        if teach_test and status=='optimal':
            print('Teacher test SUCCESS.')
        else:
            print('Teacher test FAILED. Failed instances: ', teach_fail)

        # Maturity Test
        mat_test, mat_fail = tt.test_maturity(n_p_,n_d_,n_s_, sol_, M_, demand_)
        if mat_test and status=='optimal':
            print('Maturity test SUCCESS.')
        else:
            print('Maturity test FAILED. Failed instances: ', mat_fail)

        # No Repeat Test
        rep_test, rep_fail = tt.test_not_repeated(n_p_,n_d_,n_s_, sol_)
        if rep_test and status=='optimal':
            print('No Repeat test SUCCESS.')
        else:
            print('No Repeat test FAILED. Failed instances: ', rep_fail)

        # Slot choice Test
        slot_test, slot_fail = tt.test_slot_choice(n_p_,n_d_,n_s_, sol_, slot_choice_)
        if slot_test and status=='optimal':
            print('Slot Choice test SUCCESS.')
        else:
            print('Slot Choice test FAILED. Failed instances: ', slot_fail)

        # Forced choice Test
        force_test, force_fail = tt.test_force(n_p_,n_d_,n_s_, sol_, force_)
        if slot_test and status=='optimal':
            print('Forced test SUCCESS.')
        else:
            print('Forced test FAILED. Failed instances: ', slot_fail)




