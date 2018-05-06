from cvxpy import *

x = Variable()
y = Variable()

constraints = [x + y == 1, x - y >= 1]

obj = Minimize(square(x - y))

prob = Problem(obj, constraints)
prob.solve()
print("status: ", prob.status)
print('optimal value ', prob.value)
print('optimal var ', x.value, y.value)
print('\n')

prob.objective = Maximize(x + y)
print('optimal value', prob.solve())

prob.constraints[0] = (x + y <= 3)
print('optimal value', prob.solve())
