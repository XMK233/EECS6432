import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

data = pd.read_csv('dataop-pi_data-gathering_2018-12-18_18-15-36.csv')
data.head()
data.info()
data.describe()
data.columns

print(data)

x = np.asarray(data['input']).reshape(-1, 1)
y = np.asarray(data['cpu_usage']).reshape(-1, 1)


# create a linear regression model
model = LinearRegression()
model.fit(x, y)

print(model.score(x, y))
print(model.predict(np.array([[0]])))
print('D is ')
print(model.predict(np.array([[1]]))-model.predict(np.array([[0]])))

# Plot outputs
plt.scatter(x, y,  color='blue')
plt.plot(x, model.predict(x), color='red', linewidth=3)

plt.xticks(())
plt.yticks(())

plt.show()