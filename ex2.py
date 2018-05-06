from cvxpy import *
import numpy as np

X = Bool(3,4)


b = np.asarray([[2],[3],[2]])
constraints = [sum_entries(X, axis=1) >= b, X[0,0] == 0, X[1,2]==0, X[2,0]==0]

obj = Minimize(max_entries(sum_entries(X, axis=0)))

prob = Problem(obj, constraints)
prob.solve()

print("status:", prob.status)
print("optimal value", prob.value)
print('optimal var \n', X.value)