# -*- coding=utf-8 -*-
# A servable model trained by keras
# with plot
# continous updating and delivering. This code need further refinement

import tensorflow as tf
from tensorflow.python.keras import backend as K
from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import tag_constants, signature_constants, signature_def_utils_impl
from tensorflow.python.keras.models import Sequential, load_model
from tensorflow.python.keras.layers import Dense
import matplotlib as plt
import datetime

import pandas as pd

sess = tf.Session()
K.set_session(sess)
K.set_learning_phase(0)

f = open("model_version", "r")
last_version = str(int(f.readline().strip()))
new_version = str(int(last_version) + 1)
f.close()

tf.saved_model.loader.load(sess, [tag_constants.SERVING], "ctnnum_model/%s" %(last_version))
graph = tf.get_default_graph()
for op in graph.get_operations():
    print(op.name)
x = graph.get_tensor_by_name("inputs:0")
y = graph.get_tensor_by_name("prediction:0")
print(sess.run(y, {x: [0, 0, 0]}))
#last_model = load_model("ctnnum_model/%s/saved_model.pb" %(last_version))
'''f = open("model_version", "w")
f.write(new_version)
f.close()
epoch = 1000
batch_size = 20

X_train = pd.read_pickle("X_train.pkl")
X_test = pd.read_pickle("X_test.pkl")
y_train = pd.read_pickle("y_train.pkl")
y_test = pd.read_pickle("y_test.pkl")

history = last_model.fit(X_train, y_train, epochs=epoch, batch_size=batch_size,  verbose=1, validation_split=0.2)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper right')
plt.savefig("images\\%s.png" %(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
plt.show()

x = last_model.input
y = last_model.output

prediction_signature = \
    tf.saved_model.signature_def_utils.predict_signature_def(
        {"inputs": x},
        {"prediction":y}
    )
valid_prediction_signature = \
    tf.saved_model.signature_def_utils.is_valid_signature(prediction_signature)
builder = saved_model_builder.SavedModelBuilder('./ctnnum_model/'+ last_model)
builder.add_meta_graph_and_variables(
      sess, [tag_constants.SERVING],
      signature_def_map={
           signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: prediction_signature,
      })
builder.save()'''