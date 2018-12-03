# pid
import numpy as np

Kp = 0.3
Ki = 0.15
Kd = 0

Y = 10

K = 0.3

e0 = -6
y0 = 15

n = 5

y = y0
e_history = [e0]

for x in range(1, n+1):
    print('e%s: ' %(x))
    e = Y - y
    e_history.append(e)    
    print(e_history[-1])
    u = Kp*e
    u = u + Ki * np.sum(e_history)
    u = u + Kd*(e - (e_history[(len(e_history)-2)]))
    print('u%s'  %(x))
    print('%s'  %(u))
    y = y + K * u
    print('y%s: ' %(x))
    print('%s' %(y))

    print('')