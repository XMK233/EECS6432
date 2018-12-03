import numpy as np

# 2-D array: 1 x 1
A = np.array([[1]])
# 2-D array: 1 x 1
B = np.array([[0.2]])
# 2-D array: 1 x 1
C = np.array([[1]])
# 2-D array: 1 x 1
X = np.array([[3]])
# 2-D array: 1 x 1
Y_next = np.array([[4]])

X_next = np.dot(np.linalg.pinv(C), Y_next)
print('X_next: ')
print(X_next)

U = np.dot(np.linalg.pinv(B), X_next - np.dot(A, X))
print('U: ')
print(U)
