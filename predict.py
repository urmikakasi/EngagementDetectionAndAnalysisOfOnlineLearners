import threading
import matplotlib.pyplot as plt
import os, time, sys
import shutil
import numpy as np
import random
import tensorflow as tf
import copy
import time
from global_variable import i
from class1 import split
import md_config as cfg
from feature_collection import FeatureCollection
import pandas as pd


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed, GlobalAveragePooling1D, Activation, Concatenate, InputLayer, PReLU

interval_duration = 10.0

def define_model(hparams, model_name):
	current_n_lstms = hparams['NUM_LSTM_LAYERS']
	current_lstm_units = hparams['LSTM_UNITS']
	current_n_denses = hparams['NUM_DENSE_LAYERS']
	current_dense_units = hparams['DENSE_UNITS']
	current_dropout_rates = hparams['DROPOUT_RATES']
	current_time_step = hparams['TIME_STEP']
	current_input_units = hparams['INPUT_UNITS']
	current_densen_act = hparams['ACTIVATION_F']

	model = Sequential()
	if hparams['FC1'][1] > 0:
		model.add(TimeDistributed(Dense(hparams['FC1'][1], activation='relu'),
								  input_shape=(current_time_step, hparams['FC1'][0])))

	model.add(
		LSTM(current_lstm_units[0], return_sequences=True, 
	   input_shape=(current_time_step, current_input_units),
				  stateful=False))

	if current_n_lstms > 1:
		for idx in range(1, current_n_lstms):
			model.add(LSTM(current_lstm_units[idx], return_sequences=True))

	for idx in range(current_n_denses):
		model.add(TimeDistributed(Dense(current_dense_units[idx], activation='relu')))

	model.add(TimeDistributed(Dense(1, activation=current_densen_act)))
	model.add(GlobalAveragePooling1D())

	return model

def get_model(model_index, n_segments=15, input_units=60):
    
    ld_cfg = cfg.md_cfg
    hparams = copy.deepcopy(ld_cfg[model_index])
    ft_type = 'of'


    hparams['TIME_STEP'] = n_segments
    hparams['INPUT_UNITS'] = hparams['FC1'][1] if hparams['FC1'][1] > 0 else input_units
    hparams['optimizer'] = 'adam'
    hparams['ACTIVATION_F'] = 'tanh'
    hparams['CLSW'] = 1

    cur_model = define_model(hparams,hparams['NAME'])
    cur_model.build()
    cur_model.load_weights(
            './models/{}_{}_models_{}_{}_0_epochs{}_best_weight.h5'.format(hparams['model_path'], ft_type,
                                                                           hparams['n_segments'], hparams['alpha'],
                                                                           hparams['EPOCHS']))

    return cur_model

def periodic_function():
	duration = time.strftime("%M:%S", time.gmtime(int(time.time() - start_time)))
	if os.path.isdir("processed"):
		feature_extraction = FeatureCollection('processed')
		ft = np.array(feature_extraction.get_all_data())
		
		
		with session1.as_default():
			with graph1.as_default():
				v1 = eye_gaze_v1.predict(ft[i].reshape(1,15,60))
	
		with session2.as_default():
			with graph2.as_default():		
				v2 = eye_gaze_v2.predict(ft[i].reshape(1,15,60))
	
		print('v1 and v2 {} {}'.format(v1,v2))
		enga_score = 0.5 * (v1 + v2)
		print('engagement_score = {}'.format(enga_score))
		x.append(duration)
		if enga_score < 0.4:
			y.append(0)
		elif enga_score < 0.6:
			y.append(1)
		elif enga_score < 0.83:
			y.append(2)
		else:
			y.append(3)
		print(x)
		print(y)
		shutil.rmtree('../../OpenFace/build/processed', ignore_errors=True)

def startTimer():
	threading.Timer(interval_duration,startTimer).start()
	periodic_function()

if __name__ == '__main__':
	x = []
	y = []
	
	file = os.listdir('processed')
	ext="processed/"
	in_csv=ext+str(file[0])
	#get the number of lines of the csv file to be read
	number_lines = sum(1 for row in (open(in_csv)))
	#size of rows of data to write to the csv, 
	#you can change the row size according to your need
	rowsize = 200
	#start looping through data writing it to a new file for each set
	for i in range(1,number_lines,rowsize):
	
		df = pd.read_csv(in_csv,
	
			  header=None,
	
			  nrows = rowsize,#number of rows to read at each loop
	
			  skiprows = i)#skip rows that have been read
	
	
	#csv to write data to a new file with indexed name. input_1.csv etc.
	
		out_csv = 'processed/input' + str(i) + '.csv'
	
	
		df.to_csv(out_csv,
	
			  index=False,
	
			  header=False,
	
			  mode='a',#append data to csv file
	
			  chunksize=rowsize)#size of data to append for each loop

	os.remove(in_csv)
	
	
	graph1 = tf.Graph()
	with graph1.as_default():
		session1 = tf.Session()
		with session1.as_default():
			eye_gaze_v1 = get_model(model_index=0)
	graph2 = tf.Graph()
	with graph2.as_default():
		session2 = tf.Session()
		with session2.as_default():
			eye_gaze_v2 = get_model(model_index=1)


	start_time = time.time()
	for i in range(0,20):
		startTimer()
		i+=1
		if i==7:
			break
		#while True:
		plt.yticks(np.arange(4), ('Disengaged', 'Barely Engaged', 'Engaged', 'Highly Engaged'))
		plt.xticks(rotation=90)
		plt.step(x, y, 'b')
		plt.pause(1)
		

	


