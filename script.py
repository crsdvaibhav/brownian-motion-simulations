import numpy as np
import matplotlib.pyplot as plt

"""
For time:
0.01-0.1
0.1-1
1-10
10-100
with 10 in each range
"""
activity = 3
neta = 3
epsilon = 0.5

time = np.array([])
for i in [0.01, 0.1, 1, 10]:
    number = 10
    if i >= epsilon:
        number = i*10 / epsilon
    time = np.concatenate((time, np.linspace(i, i*10, int(number))[:-1]))

time = np.append(time, 100)

theta = 0
angluar_velocity = np.random.uniform(-neta, neta)
x = np.array([0])
y = np.array([0])
msd = np.array([])

prevTime = 0
for currTime in time:
    dt = currTime - prevTime

    # After every epsilon time, randomly select a new angular velocity
    if (currTime % epsilon) == 0.0:
        angluar_velocity = np.random.uniform(-neta, neta)

    dtheta = angluar_velocity * dt
    theta = theta + dtheta

    x_dot = activity * np.cos(theta)
    y_dot = activity * np.sin(theta)

    dx = x_dot * dt
    dy = y_dot * dt

    x = np.append(x, x[-1] + dx)
    y = np.append(y, y[-1] + dy)

    msd = np.append(msd, np.mean((x - x[0])**2 + (y - y[0])**2))

    prevTime = currTime


plt.loglog(time, msd)
plt.show()


