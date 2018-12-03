#observible?
import numpy as np

# 2-D array: 3 x 3
A = np.array([[1, 2, 3], [4, 5, 6], [1, 2, 3]])
# 2-D array: 3 x 2
B = np.array([[1, 2], [3, 4], [1, 2]])
# 2-D array: 1 x 3
C = np.array([[1, 2, 3]])
# 2-D array: 3 x 1
X = np.array([[1], [3], [5]])
# 2-D array: 2 x 1
U = np.array([[1], [3]])

n = X.shape[0]
#O = np.empty((0, 3))
print("O: ")
for i in range(n):
    #O = np.vstack([O, np.dot(C, np.linalg.matrix_power(A, i))])
    print(np.dot(C, np.linalg.matrix_power(A, i)).astype(int))

#print(O.astype(int))