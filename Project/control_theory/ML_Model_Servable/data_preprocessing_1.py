import pandas as pd
import sys
sys.path.append("..")
from sklearn.model_selection import train_test_split

#------------ Data preprocess -------------------------
df=pd.read_csv('../raw_data/2018-12-22_00-43-41.csv',header=0,sep=',')
df["Res"] = df["Res"] / 1000000
df = df[df["Xw"] >= 10]
x = df[["Uw_cpu", "Xw", "Res"]]
y=df[["CtnNum"]]
X_train, X_test, y_train, y_test = train_test_split(x, y)
print(X_train, y_train)

X_train.to_pickle("X_train.pkl")
X_test.to_pickle("X_test.pkl")
y_train.to_pickle("y_train.pkl")
y_test.to_pickle("y_test.pkl")


'''df["Cnew"] = -1
df["Unew"] = -1
df["Xnew"] = -1
df[["Unew", "Xnew", "Res"]] = df[["Unew", "Xnew", "Res"]].astype(float)
df["Res"] = df["Res"] #/ 100000
df = df[["Uw_cpu", "Xw", "Unew", "Xnew", "CtnNum", "Cnew", "Res"]]
length = len(df)
for i in range(length):
    if i == length - 1:
        continue
    df["Unew"][i] = df["Uw_cpu"][i + 1]
    df["Xnew"][i] = df["Xw"][i + 1]
    df["Cnew"][i] = df["CtnNum"][i + 1]
x=df[["Uw_cpu", "Xw", "Unew", "Xnew", "CtnNum", "Cnew"]]
y=df[["Res"]]
X_train, X_test, y_train, y_test = train_test_split(x, y)

X_train.to_pickle("X_train.pkl")
X_test.to_pickle("X_test.pkl")
y_train.to_pickle("y_train.pkl")
y_test.to_pickle("y_test.pkl")'''









#-------------------Model training-------------------
'''import tensorflow as tf

INPUT_NODE = 6
OUTPUT_NODE = 1
LAYER1_NODE = 4
LAYER2_NODE = 2

BATCH_SIZE = 10
LEARNING_RATE_BASE = 0.8
LEARNING_RATE_DECAY = 0.99
REGULARIZATION_RATE = 0.0001
TRAINING_STEPS = 5000
#MOVING_AVERAGE_DECAY = 0.99

x = tf.placeholder(tf.float32, shape = (None, INPUT_NODE))
y_ = tf.placeholder(tf.float32, shape = (None, 1))

weights1 = tf.get_variable("weights1",
                           [INPUT_NODE, LAYER1_NODE],
                           initializer=tf.truncated_normal_initializer(stddev=0.1))
biases1 = tf.get_variable("biases1", [LAYER1_NODE], initializer=tf.constant_initializer(0.0))
layer1 = tf.nn.relu(tf.matmul(x, weights1) + biases1)

weights2 = tf.get_variable("weights2",
                           [LAYER1_NODE, LAYER2_NODE],
                           initializer=tf.truncated_normal_initializer(stddev=0.1))
biases2 = tf.get_variable("biases2", [LAYER1_NODE], initializer=tf.constant_initializer(0.0))
layer2 = tf.matmul(layer1, weights2) + biases2

weights3 = tf.get_variable("weights3",
                           [LAYER2_NODE, OUTPUT_NODE],
                           initializer=tf.truncated_normal_initializer(stddev=0.1))
biases3 = tf.get_variable("biases3", [LAYER1_NODE], initializer=tf.constant_initializer(0.0))
y = tf.matmul(layer2, weights3) + biases3

cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits \
        (logits=y, labels=y_)
cross_entropy_mean = tf.reduce_mean(cross_entropy)

train_step = \
        tf.train.GradientDescentOptimizer(LEARNING_RATE_BASE) \
            .minimize(cross_entropy_mean)

with tf.Session() as sess:
    tf.global_variables_initializer().run()
    for i in range(TRAINING_STEPS):'''

