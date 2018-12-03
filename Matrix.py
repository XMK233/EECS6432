import numpy as np

# 2-D array: 3 x 3
A = np.array([[1,2,3], [4,5,6], [1,2,3]])
# 2-D array: 3 x 2
B = np.array([[1,2], [3,4], [1,2]])
# 2-D array: 1 x 3
C = np.array([[1,2,3]])
# 2-D array: 3 x 1
X = np.array([[1], [3], [5]])
# 2-D array: 2 x 1
U = np.array([[1], [3]])

n = 3

for x in range(0, n+1):
    print('X%s: ' %(x))
    print('%s' %(X))
    Y = np.dot(C, X)
    print('Y_%s: ' %(x))
    print('%s' %(Y))
    X = np.dot(A, X) + np.dot(B, U)
    print('')



















