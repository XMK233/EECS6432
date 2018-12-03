#(don't know the rationle)
import numpy as np

lambda_m = np.array([0.1 , 0.1, 1])

D = np.array([[0.1, 0.15, 0.2], [0.3, 0.4, 0.6], [0.3, 0.4, 0.6]])

Ud = np.dot(lambda_m, D)

Rdc = D/(1-Ud)

Rc = np.sum(Rdc, axis=1)

print(Ud)
print(Rdc)
print(Rc)