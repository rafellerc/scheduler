import numpy as np
from random import randint

def test_indisp(n_p, n_d, n_s, sol, indisp):
    """Tests a solution to check if all the indisponibilities are respected.
    Note that the indisponibilities are based on days, not slots.

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.
        indisp: [list] A list of tuples each containing the person and day
        of indisponibility.

    Returns:
        bool: True if the solution does not disrespect any indisponibily and
        False otherwise.
    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    passed = True
    for p, d in indisp:
        for i in range(n_s):
            if sol[p, n_s*d + i] != 0:
                passed = False   
    return passed

def test_gender(n_p, n_d, n_s, sol, gender, demand, prop):
    """Tests a solution to check if the max limit of men is respected.
    The backup slots (demand of 1) are not taken into account.

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.
        gend: [ndarray] The corresponding genders of the people in the list. Men
        are represented by ones and women by zeros.
        demand: [ndarray] The row vector of the demand of personnel for each slot. 
        prop: [float] The max proportion of men allowed, used with a floor function

    Returns:
        bool: True if the solution does respects the max limit of men per slot and
        False otherwise.
        inst_fail: A list of instances on which the test failed
    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    assert gender.shape == (n_p,), ("The given gender vector does not has the " +
        "correct shape, needed {}, got {}".format((n_p,), gend.shape))
    assert demand.shape == (n_d*n_s,), ("The given demand vector does not has the " +
        "correct shape, needed {}, got {}".format((n_d*n_s,), demand.shape))
    passed = True
    inst_fail = []

    for s in range(n_d*n_s):
        n_men = np.dot(sol[:, s].reshape(1,-1), gender.reshape(-1,1)).squeeze()
        if n_men > prop * demand[s] and demand[s] > 1:
            passed = False
            inst_fail.append(s)

    # Question: Return or not the fail instances?
    return passed, inst_fail

def test_demand(n_p, n_d, n_s, sol, demand):
    """Tests a solution to check if the demand of people is met.

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.
        demand: [ndarray] The row vector of the demand of personnel for each slot. 

    Returns:
        bool: True if the solution meets the demand for each slot
        False otherwise.
        inst_fail: A list of instances on which the test failed
    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    assert demand.shape == (n_d*n_s,), ("The given demand vector does not has the " +
        "correct shape, needed {}, got {}".format((n_d*n_s,), demand.shape))
    passed = True
    inst_fail = []

    for s in range(n_d*n_s):
        total_pers = np.sum(sol[:, s])
        if total_pers != demand[s]:
            passed = False
            inst_fail.append(s)

    # Question: Return or not the fail instances?
    return passed, inst_fail

def test_not_repeated(n_p, n_d, n_s, sol):
    """Tests a solution to check that no one is scheduled to more than one slot
    in the same day

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.

    Returns:
        bool: True if the solution doesn't repeat anyone in the same day
        False otherwise.
        inst_fail: A list of instances on which the test failed.
            The instances are organized as (person, day)
    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    passed = True
    inst_fail = []

    for d in range(n_d):
        total_work = np.sum(sol[:, d*n_s:n_s*(d+1)], axis=1)
        for p in range(n_p):
            if total_work[p] > 1:
                passed = False
                inst_fail.append((p, d))

    # Question: Return or not the fail instances?
    return passed, inst_fail

def test_maturity(n_p, n_d, n_s, sol, matur, demand):
    """Tests a solution to check if each slot (excluding backup) has at least
    one mature member.

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.
        matur: [ndarray] The corresponding maturity of the people in the list. Married
        people with kids are represented by ones otherwise by zeros.
        demand: [ndarray] The row vector of the demand of personnel for each slot.

    Returns:
        bool: True if the solution has at least one mature member per slot
        False otherwise.
        inst_fail: A list of instances on which the test failed
    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    assert matur.shape == (n_p,), ("The given maturity vector does not has the " +
        "correct shape, needed {}, got {}".format((n_p,), matur.shape))
    assert demand.shape == (n_d*n_s,), ("The given demand vector does not has the " +
        "correct shape, needed {}, got {}".format((n_d*n_s,), demand.shape))
    passed = True
    inst_fail = []

    for s in range(n_d*n_s):
        n_mature = np.dot(sol[:, s].reshape(1,-1), matur.reshape(-1,1)).squeeze()
        if n_mature == 0 and demand[s] > 1:
            passed = False
            inst_fail.append(s)

    # Question: Return or not the fail instances?
    return passed, inst_fail

def test_teacher(n_p, n_d, n_s, sol, teach, demand, max_teach=1):
    """Tests a solution to check if each slot (excluding backup) has at least
    one teacher.

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.
        teacher: [ndarray] The corresponding teacher status of the people in the list.
        Teacher are represented by ones otherwise by zeros.
        demand: [ndarray] The row vector of the demand of personnel for each slot.
        max_teach: [int] Maximum number of teachers by slot. Default value = 1

    Returns:
        bool: True if the solution has at least one teacher member per slot
        False otherwise.
        inst_fail: A list of instances on which the test failed
    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    assert teach.shape == (n_p,), ("The given teacher vector does not has the " +
        "correct shape, needed {}, got {}".format((n_p,), teach.shape))
    assert demand.shape == (n_d*n_s,), ("The given demand vector does not has the " +
        "correct shape, needed {}, got {}".format((n_d*n_s,), demand.shape))
    passed = True
    inst_fail = []

    for s in range(n_d*n_s):
        n_teach = np.dot(sol[:, s].reshape(1,-1), teach.reshape(-1,1)).squeeze()
        if (n_teach == 0 or n_teach > max_teach) and demand[s] > 1:
            passed = False
            inst_fail.append(s)

    # Question: Return or not the fail instances?
    return passed, inst_fail

def test_slot_choice(n_p, n_d, n_s, sol, slot_choice):
    """Tests a solution to check if each person's slot choice was respected.

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.
        slot_choice: [ndarray] Matrix of choice vectors, each row correspond
        to the choice of the person of participating (1) or not (0) in a
        given type of activity.

    Returns:
        bool: True if the solution respects all of the slot choices
        False otherwise.
        inst_fail: A list of instances on which the test failed
                The instances are organized as (person, day)

    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    assert isinstance(slot_choice, np.ndarray), "The given slot_choice matrix is not a numpy array."
    assert slot_choice.shape == (n_p, n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Matrix was ({}) expected ({},{}) "
        .format(slot_choice.shape,n_p,n_s))
    passed = True
    inst_fail = []

    for d in range(n_d):
        for p in range(n_p):
            chx_vec = slot_choice[p, :]
            diff_vec = np.int16(chx_vec.reshape(-1)) - np.int16(sol[p, d*n_s:n_s*(d+1)].reshape(-1))
            if -1 in diff_vec:
                passed = False
                inst_fail.append((p, d))

    # Question: Return or not the fail instances?
    return passed, inst_fail

def test_force(n_p, n_d, n_s, sol, force):
    """Tests a solution to check if all the pre-allocated people are in
    correctly allocated in the solution 

    Args:
        n_p: [int] Number of people in the list
        n_d: [int] Number of days in final solution
        n_s: [int] Number of slots in each day
        sol: [ndarray] The solution to the optimization problem, normally a 
        2D matrix of zeros and ones in which each row corresponds to a 
        person and each row to a slot.
        force: [list] List of tuples (person, day*n_s + slot) which mean 
        that we are forcing person to be on slot on the given day.

    Returns:
        bool: True if the solution respects the preallocation
        False otherwise.
        inst_fail: A list of instances on which the test failed
                The instances are organized as (person, day*n_s + slot)

    """
    assert isinstance(sol, np.ndarray), "The given solution is not a numpy array."
    assert sol.shape == (n_p, n_d*n_s), ("The informed dimensions are not" +
        "consistent with the given solution. Informed dimensions were, " +
        "n_p: {}, n_d: {}, n_s: {}".format(n_p,n_d,n_s))
    passed = True
    inst_fail = []

    for p, s in force:
        if sol[p, s] != 1:
            passed = False
            inst_fail.append((p,s))

    return passed, inst_fail



if __name__ == "__main__":
    pass
    # Test indisp.
    # sol_ = np.random.choice([0, 1], size=([2,9]), p=[0.7, 0.3])
    # print("Solution: \n", sol_, "\n")
    # indisp_ = []
    # for k in range(2):
    #     p_ = randint(0,1)
    #     d_ = randint(0,2)
    #     indisp_.append((p_,d_))
    # print("Indisponibilites", indisp_)
    # passed_ = test_indisp(2, 3, 3, sol_, indisp_)
    # if passed_:
    #     print('Solution passed on indisponibility test')
    # else:
    #     print('Solution did NOT pass on indisponibility test')

    # Test gender
    # sol_ = np.random.choice([0, 1], size=([6,4]), p=[0.6, 0.4])
    # gender_ = np.random.choice([0, 1], size=([6]), p=[0.5, 0.5])
    # demand_ = np.asarray([2,1,2,1])
    # passed_, fail = test_gender(6, 2, 2, sol_, gender_, demand_, 0.5)
    # print(sol_)
    # print(gender_)
    # print(passed_, fail)

    # Test demand
    # sol_ = np.random.choice([0, 1], size=([4,2]), p=[0.7, 0.3])
    # demand_ = np.asarray([2,1])
    # passed_, fail = test_demand(4, 1, 2, sol_, demand_)
    # print(sol_)
    # print(passed_, fail)

    # Test not Repeated
    # sol_ = np.random.choice([0, 1], size=([4,6]), p=[0.7, 0.3])
    # passed_, fail = test_not_repeated(4, 2, 3, sol_)
    # print(sol_)
    # print(passed_, fail)

    # Test Maturity
    # sol_ = np.random.choice([0, 1], size=([6,4]), p=[0.6, 0.4])
    # matur_ = np.random.choice([0, 1], size=([6]), p=[0.8, 0.2])
    # demand_ = np.asarray([2,1,2,1])
    # passed_, fail = test_maturity(6, 2, 2, sol_, matur_, demand_)
    # print(sol_)
    # print(matur_)
    # print(passed_, fail)

    # Test teach
    # sol_ = np.random.choice([0, 1], size=([6,4]), p=[0.6, 0.4])
    # teach_ = np.random.choice([0, 1], size=([6]), p=[0.5, 0.5])
    # demand_ = np.asarray([2,1,2,1])
    # passed_, fail = test_teacher(6, 2, 2, sol_, teach_, demand_)
    # print(sol_)
    # print(teach_)
    # print(passed_, fail)

    # Test slot_choice
    # sol_ = np.random.choice([0, 1], size=([4,4]), p=[0.6, 0.4])
    # slot_choice_ = np.random.choice([0, 1], size=([4,2]), p=[0.2, 0.8])
    # demand_ = np.asarray([2,1,2,1])
    # passed_, fail = test_slot_choice(4, 2, 2, sol_, slot_choice_)
    # print(sol_)
    # print(slot_choice_)
    # print(passed_, fail)

    # Test Force
    # sol_ = np.random.choice([0, 1], size=([4,4]), p=[0.3, 0.7])
    # force_ = []
    # for k in range(2):
    #     p_ = randint(0,3)
    #     s_ = randint(0,3)
    #     force_.append((p_,s_))
    # passed_, fail = test_force(4, 2, 2, sol_, force_)
    # print(sol_)
    # print(force_)
    # print(passed_, fail)
