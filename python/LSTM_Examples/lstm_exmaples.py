#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 14:41:18 2020

@author: glenn
"""


from pprint import pprint
import numpy as np
from numpy import array
from keras.models import Model, Sequential
from keras.layers import Dense, Input, LSTM, TimeDistributed


length = 5
seq = array([i/float(length) for i in range(length)])


#------------------------------------------------------------------------------   
#1 to 1 LSTM for sequence predicition
X = seq.reshape(length, 1, 1)
y = seq.reshape(length, 1)

n_neurons = length
n_batch = length
n_epoch = 1000

model = Sequential()
model.add(LSTM(n_neurons, input_shape=(1,1)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
print(model.summary())

model.fit(X, y, epochs=n_epoch, batch_size=n_batch, verbose=2)

result = model.predict(X, batch_size=n_batch, verbose=0)
for val in result:
    print('%.1f' % val)
    
    
#------------------------------------------------------------------------------   
#many to many LSTM for sequence prediction (without TimeDistributed)
X = seq.reshape(1, length,1)
y = seq.reshape(1, length)

n_neurons = length
n_batch = 1
n_epoch = 500
    
model1 = Sequential()
model1.add(LSTM(n_neurons, input_shape=(length,1)))
model1.add(Dense(length))
model1.compile(loss='mean_squared_error', optimizer='adam')
print(model1.summary())  

model1.fit(X, y, epochs=n_epoch, batch_size=n_batch, verbose=2)

result = model1.predict(X, batch_size=n_batch, verbose=0)
for val in result[0,:]:
    print('%.1f' % val)
 
    
#------------------------------------------------------------------------------       
#many to many LSTM for sequence prediction (with TimeDistributed)
X = seq.reshape(1, length, 1)
y = seq.reshape(1, length, 1)

n_neurons = length
n_batch = 1
n_epoch = 1000

model2 = Sequential()
model2.add(LSTM(n_neurons, input_shape=(length, 1), return_sequences=True))
model2.add(TimeDistributed(Dense(1)))
model2.compile(loss='mean_squared_error', optimizer='adam')
print(model2.summary())

model2.fit(X, y, epochs=n_epoch, batch_size=n_batch, verbose=2)

result = model2.predict(X, batch_size=n_batch, verbose=0)
for val in result[0,:,0]:
    print('%.1f' % val)


#------------------------------------------------------------------------------
#many to many LSTM for string sequence prediction (with TimeDistributed)
sequences = [['a', 'b', 'c'],
             ['b', 'c', 'd'],
             ['a', 'b', 'c', 'd'],
             ['b', 'c', 'd', 'e'],
             ['a', 'b', 'c', 'd', 'e']]

A = ['a', 'b', 'c', 'd', 'e', '-']
activity_to_index = dict((c,i) for i, c in enumerate(A))
index_to_activity = dict((i,c) for i, c in enumerate(A))

n_samples = len(sequences)
max_seq_len = max([len(seq) for seq in sequences])
n_features = len(A)

#training data X in shape (samples, time steps, features)
#so here: (5, 5, 4); cause 5 samples, with 5 timesteps each (max_seq_len) and #features=vocab_sizes

X = np.zeros((n_samples, max_seq_len, n_features))
y = np.zeros((n_samples, max_seq_len, n_features))

for i in range(len(sequences)):
    for j in range(len(sequences[i])):
        X[i][j][activity_to_index[sequences[i][j]]] = 1.0
        y[i][j][activity_to_index[sequences[i][j]]] = 1.0
    
n_neurons = max_seq_len
n_epoch = 1000

model3 = Sequential()
model3.add(LSTM(n_neurons, input_shape=(max_seq_len, n_features), return_sequences=True))
model3.add(TimeDistributed(Dense(n_features, activation='softmax')))
model3.compile(loss='mean_squared_error', optimizer='adam')
print(model3.summary())

model3.fit(X, y, epochs=n_epoch)

result = model3.predict(X) #X[0].reshape(1, X[0].shape[0], X[0].shape[1])

predicted_traces = []
for i in range(result.shape[0]):
    predicted_trace = []
    for j in range(result.shape[1]):
        idx = np.argmax(result[i][j])
        if np.all(X[i][j] == 0.0):
            idx = len(A) - 1
        predicted_trace.append(index_to_activity[idx])
    predicted_traces.append(predicted_trace)
