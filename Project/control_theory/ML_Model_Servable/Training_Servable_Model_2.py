# A servable model trained by keras, initialized training. 
# with plot

import tensorflow as tf
from tensorflow.python.keras import backend as K
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants, signature_def_utils_impl
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
import matplotlib as plt
import datetime

import pandas as pd

sess = tf.Session()
K.set_session(sess)
K.set_learning_phase(0)

f = open("model_version", "r")
model_version = str(int(f.readline().strip()) + 1)
f.close()
f = open("model_version", "w")
f.write(model_version)
f.close()
epoch = 100
batch_size = 20

X_train = pd.read_pickle("X_train.pkl")
X_test = pd.read_pickle("X_test.pkl")
y_train = pd.read_pickle("y_train.pkl")
y_test = pd.read_pickle("y_test.pkl")

model = Sequential()
model.add(Dense(12, input_dim=3, kernel_initializer='normal', activation='relu'))
'''model.add(Dense(10, activation='relu'))
model.add(Dense(12, activation='relu'))'''
model.add(Dense(10, activation='relu'))
model.add(Dense(1, activation='linear'))
model.summary()

model.compile(loss='mse', optimizer='adam', metrics=['mse','mae'])
history = model.fit(X_train, y_train, epochs=epoch, batch_size=batch_size,  verbose=1, validation_split=0.2)

'''plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper right')
plt.savefig("images\\%s.png" %(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
plt.show()'''

x = model.input
y = model.outputs

prediction_signature = \
    tf.saved_model.signature_def_utils.predict_signature_def(
        {"inputs": x},
        {"prediction":y}
    )
valid_prediction_signature = \
    tf.saved_model.signature_def_utils.is_valid_signature(prediction_signature)
'''if(valid_prediction_signature == False):
    raise ValueError("Error: Prediction signature not valid!")'''
builder = saved_model_builder.SavedModelBuilder('./ctnnum_model/'+model_version)
builder.add_meta_graph_and_variables(
      sess, [tag_constants.SERVING],
      signature_def_map={
           signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:prediction_signature,
      })
builder.save()