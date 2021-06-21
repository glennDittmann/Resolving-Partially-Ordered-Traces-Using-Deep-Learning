import numpy as np
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from itertools import combinations, combinations_with_replacement, product, permutations
import datetime


NAME = "concept:name"
TIME = "time:timestamp"

def trace_is_certain(trace):
  """ Checks if a trace is certain, gets called by split log """
  for i in range(len(trace)-1):
    if trace[i][TIME] == trace[i+1][TIME]:
      return False
  return True
  
def split_log(log):
  """ Splits a log in two logs, the one holding only totally ordered traces and one holding only partially ordered traces. """
  certain_log, uncertain_log = [], []
  
  for trace in log:
      if trace_is_certain(trace):
        certain_log.append(trace)
      else:
        uncertain_log.append(trace)
  
  return certain_log, uncertain_log

def split_log_seconds(log):
  c_log, u_log = [], []
  for trace in log:
    uncertain = False
    timestamps = []
    for event in trace:
      if abstract_microseconds(event['time:timestamp']) in timestamps:
        uncertain = True
        break
      else:
        timestamps.append(abstract_microseconds(event['time:timestamp']))
    if uncertain:
      u_log.append(trace)
    else:
      c_log.append(trace)
  return c_log, u_log

def get_sparse_log(log):
  "From the log object extracts only the activity sequences, i.e. traces, as lists of strings."
  sparse_log = []
  for trace in log:
    temp_trace = []
    for event in trace:
      temp_trace.append(event["concept:name"])
    sparse_log.append(temp_trace)
    
  return sparse_log

def get_sparse_log_set(log) -> list:
  log_set = []
  for trace in log:
    log_set.append(get_sparse_trace_sets(trace))
  return log_set

def get_sparse_trace_sets(trace) -> dict:
  trace_set = dict()
  for event in trace:
    trace_set[str(event["time:timestamp"])] = trace_set.get(str(event["time:timestamp"]), []) + [event["concept:name"]]
  
  trace_set = [event_set for event_set in trace_set.values()]

  return trace_set

def get_sparse_log_set_artificial(log) -> list:
  log_set = []
  for trace in log:
    log_set.append(get_sparse_trace_sets_artificial(trace))
  return log_set

def get_sparse_trace_sets_artificial(trace) -> list:
  trace_set = []
  event_set = []
  for i in range(len(trace)-1):
    
    if trace[i][TIME] == trace[i+1][TIME]:   # if the next event has the same timestamp as this event we add this event to the event set
      event_set.append(trace[i][NAME]) 
    elif trace[i][TIME] != trace[i+1][TIME]: # if not, we add this event to the event set and add the event set to the collection of event sets and reset the event set
      event_set.append(trace[i][NAME])
      trace_set.append(event_set)
      event_set = []
    
    if i == len(trace)-2: 
        event_set.append(trace[i+1][NAME])
        trace_set.append(event_set)
  
  return trace_set

def longest_trace(log):
  max = 0
  for trace in log:
    if len(trace) > max:
      max = len(trace)

  return max

def longest_unc_seq(log_set):
  max = 0
  for trace_set in log_set:
    for event_set in trace_set:
      if len(event_set) > max:
        max = len(event_set)
  return max


def possible_uncertain_seq(activity_space: list, k: int) -> list:
  """Takes the activity space and builds all possible uncertain sequences up to length k, starting from 1."""

  unc_seq = []
  for i in range(2,k+1):
    unc_seq += [ sorted(list(tup)) for tup in combinations_with_replacement(activity_space, i)]

  return [[activity] for activity in activity_space] + sorted(unc_seq, key=len)

def possible_resolutions(activity_space: list, k: int) -> list:
  """Takes the activity space and builds all possible sequences up to length k, starting from 1."""

  pos_res = []
  for i in range(2,k+1):
    pos_res += [ list(tup) for tup in product(activity_space, repeat=i)]
  
  return [[activity] for activity in activity_space] + pos_res

def all_subsets(activity_space: list, k: int) -> list:
  """Takes the activity space and builds all possible uncertain sequences up to length k, starting from 1."""

  subsets = []
  for i in range(2,k+1):
    subsets += [ sorted(list(tup)) for tup in combinations(activity_space, i)]

  
  subsets = [[activity] for activity in activity_space] + sorted(subsets, key=len)
  subsets.sort()

  return list(subset for subset,_ in itertools.groupby(subsets))

def pos_res_of_event_set(event_set: list) -> list:
    """For a given events set, returns the list of all possible resolutions."""
    
    return [list(tup) for tup in permutations(event_set, len(event_set))]

def pos_res_for_unc_seq(unc_seq: list) -> dict:
    """ For all the existing uncertain sequences (of length k)
        this contains all corresponding possible resolutions.
    """
    pos_res_for_unc_seq = dict()
    for us in unc_seq:
        pos_res_for_unc_seq[tuple(us)] = pos_res_of_event_set(us)
        
    return pos_res_for_unc_seq

def old_one_hot_encode1(sparse_X, sparse_y, n_samples, max_seq_len, n_features, activity_to_index):
  X = np.zeros((n_samples, max_seq_len, n_features))
  y = np.zeros((n_samples, max_seq_len, n_features))

  for i in range(len(sparse_X)):
    for j in range(len(sparse_X[i])):
      X[i][j][activity_to_index[sparse_X[i][j]]] = 1.0
      y[i][j][activity_to_index[sparse_y[i][j]]] = 1.0

  return X, y


def old_one_hot_encode2(sparse_X, sparse_y, n_samples, max_seq_len, n_features_in, n_features_out, unc_seq_to_idx, pos_res_to_idx):
  X = np.zeros((n_samples, max_seq_len, n_features_in))
  y = np.zeros((n_samples, max_seq_len, n_features_out))

  for i in range(len(sparse_X)):
    for j in range(len(sparse_X[i])):
      X[i][j][unc_seq_to_idx[tuple(sorted(sparse_X[i][j]))]] = 1.0
      
  for i in range(len(sparse_y)):
    for j in range(len(sparse_y[i])):
      y[i][j][pos_res_to_idx[tuple(sparse_y[i][j])]] = 1.0

  return X, y

def viz_history(history, save: bool, filepath: None):
    pd.DataFrame(history.history).plot(figsize=(8, 5))
    plt.grid(True)
    plt.gca().set_ylim(-0.2, 1.2) # set the vertical range to [-0.2,-1.2]
    if save:
        plt.savefig(filepath)
    plt.show()

def decode_X(encoded_log, idx_to_act: dict, mode="enc2"):
    decoded_log = []
    
    # note that encoding one for the inputs is not injective so decoding is ambiguous
    # solution: when dividing X, y (randomly) assign the same indexes to the input log -> retain the mapping
    
    if mode == "enc2":
        for i in range(encoded_log.shape[0]):
            decoded_trace = [list(idx_to_act[np.argmax(encoded_log[i][j])])
                             for j in range(encoded_log.shape[1]) 
                             if not np.all(encoded_log[i][j]==0.0)]
            decoded_log.append(decoded_trace)
            
    if mode == "enc3":
        for i in range(encoded_log.shape[0]):
            decoded_trace = []
            for j in range(encoded_log.shape[1]):
                if not np.all(encoded_log[i][j]==0.0):
                    decoded_event = []
                    idxs = np.argwhere(encoded_log[i][j]==1).flatten().tolist() #we have multiple 1s
                    for idx in idxs: #check which idx is the original event set
                        if len(idx_to_act[idx]) > len(decoded_event):
                            decoded_event = idx_to_act[idx]
                    decoded_trace.append(list(decoded_event))
            decoded_log.append(decoded_trace)
            
    return decoded_log
    
    
def decode_y(encoded_log, idx_to_act: dict, mode: str="enc2+3"):
    decoded_log = []
    
    if mode == "enc1":
    
        for i in range(encoded_log.shape[0]):
            decoded_trace = [idx_to_act[np.argmax(encoded_log[i][j])]
                             for j in range(encoded_log.shape[1]) 
                             if not np.all(encoded_log[i][j]==0.0)]
            decoded_log.append(decoded_trace)
            
    elif mode == "enc2+3":
        
        for i in range(encoded_log.shape[0]):
            decoded_trace = [list(idx_to_act[np.argmax(encoded_log[i][j])]) 
                             for j in range(encoded_log.shape[1]) 
                             if not np.all(encoded_log[i][j]==0.0)]
            decoded_log.append(decoded_trace)

    return decoded_log

def eval_test(model, X_test, dec_y_test, dec_X_test, n_event_sets, idx_to_act: dict, pos_res_for_unc_seq: dict) -> float:
    total = X_test.shape[0]
    count = 0
    count_highest_prob_is_non_pos_res = 0
    prediction_probabilities = {}
    actual_resolution_probabilities = {}
    
    for i in tqdm(range(total)): #go over every trace in the evaluation log
        
        #get a prediction for the correct ordering of the current trace
        result = model.predict(X_test[i].reshape(1, X_test[i].shape[0], X_test[i].shape[1]))
        predicted_trace = []

        for l in range(result.shape[1]):
            if np.all(X_test[i][l] == 0.0): # ignore padding predictions
                predicted_trace.append('-')
            else:
                n_its = 0 # to monitor whether we went into while loop at least one time, i.e. the frist predction was not a pos res
                prob = np.amax(result[0][l])
                idx = np.argmax(result[0][l]) # get idx prediction with highest prob
                predicted_event = list(idx_to_act[idx]) # decode into event / sequence
                
                # check if the prediction is actually a resolution
                while not predicted_event in pos_res_for_unc_seq[tuple(sorted(dec_X_test[i][l]))]:
                    # if not take the prediction with the 2nd highest prob... etc.
                    if n_its == 0:
                        count_highest_prob_is_non_pos_res += 1
                        n_its += 1
                        
                    prob = np.amax(result[0][l])
                    result[0][l][idx] = 0.0 # set the old idx with max prob to zero
                    idx = np.argmax(result[0][l])
                    predicted_event = list(idx_to_act[idx])
                    
                    # check if all idx that had a prob > 0 where turned to 0
                    # i.e. all of the possible resolution were not considered likely at all
                    if np.all(result[0][l]==0):
                        print('BREAK: no prob...')
                        predicted_event = ['BREAK']
                        break

                predicted_trace.append(predicted_event)
                prediction_probabilities[tuple(predicted_event)] = prediction_probabilities.get(tuple(predicted_event), []) + [prob]

        predicted_trace = predicted_trace[:len(dec_y_test[i])]
        
        #print(predicted_trace, dec_y_test[i])
        if predicted_trace == dec_y_test[i]:
            count += 1

    return count/total, count_highest_prob_is_non_pos_res/n_event_sets, prediction_probabilities
    
def make_rand_predict(model, X, log_set):
    i = randint(0, len(X)-1)
    print('Trace number', i)
    print('Original Trace : ', log_set[i])

    result = model.predict(X[i].reshape(1, X[i].shape[0], X[i].shape[1])) 

    predicted_traces = []
    for k in range(result.shape[0]):
        predicted_trace = []
        for l in range(result.shape[1]):
            idx = np.argmax(result[k][l])
            #print(idx)
            if np.all(X[i][l] == 0.0):
                predicted_trace.append('-')
                #predicted_trace.append(idx_to_pos_res[idx])
            else:
                predicted_trace.append(idx_to_pos_res[idx])
        predicted_traces.append(predicted_trace)
    print()
    print('Predicted Trace:', predicted_traces)
        
def check_unc_activities(sparse_log_set: list, A: list):
    """For a given sparse log, check which events do not appear in uncertain event sets."""
    u_activities, c_activities = [], [event for event in A]
    
    for sparse_trace in sparse_log_set:
        for event_set in sparse_trace:
            if len(event_set) > 1:
                for event in event_set:
                    if event not in u_activities:
                        u_activities.append(event)
                        if event in c_activities:
                            c_activities.remove(event)
                            
    return c_activities, u_activities
                

# functions specific for Seq2Seq
def get_X_y(log, BOS, SOS):
  X, y = [], []
  for trace in log:
    temp_trace = []
    for event in trace:
      temp_trace.append(event["concept:name"])
    X.append(temp_trace)
    y.append([BOS] + temp_trace + [EOS])

  return X, y
  
  
def reverse_X(X):
  reversed_X = []
  for trace in X:
    reversed_trace = []
    for event in reversed(trace):
      reversed_trace.append(event)
    reversed_X.append(reversed_trace)
  return reversed_X

def seq2seq_encode(rev_X: list, y: list, max_enc_seq_len: int, n_enc_tok: int, max_dec_seq_len: int, n_dec_tok: int, INdict: dict, OUTdict: dict, mode: int):
    encoder_input_data = np.zeros((len(rev_X), max_enc_seq_len, n_enc_tok),dtype='float32')
    decoder_input_data = np.zeros((len(rev_X), max_dec_seq_len, n_dec_tok),dtype='float32')
    decoder_target_data = np.zeros((len(rev_X), max_dec_seq_len, n_dec_tok),dtype='float32')
    
    if mode == 1: # encoding 1
        for i, (input_trace, target_trace) in enumerate(zip(rev_X, y)):
            # ENCODER
            for t, event_set in enumerate(input_trace):
                # set 1 for all events in the event set
                idxs = list(set([INdict[tuple(event)] for event in event_set])) 
                encoder_input_data[i, t, idxs] = 1.
            # DECODER
            for t, event_set in enumerate(target_trace):
                decoder_input_data[i, t, OUTdict[tuple(event_set)]] = 1.
                if t > 0:
                    # decoder_target_data is ahead by one timestep and will not include BOS char
                    decoder_target_data[i, t - 1, OUTdict[tuple(event_set)]] = 1.
        
        return encoder_input_data, decoder_input_data, decoder_target_data 
    
    elif mode == 2: # encoding 2
        for i, (input_trace, target_trace) in enumerate(zip(rev_X, y)):
            # ENCODER
            for t, event_set in enumerate(input_trace):
                encoder_input_data[i, t, INdict[tuple(sorted(event_set))]] = 1.
            # DECODER
            for t, event_set in enumerate(target_trace):
                decoder_input_data[i, t, OUTdict[tuple(event_set)]] = 1.
                if t > 0:
                    decoder_target_data[i, t - 1, OUTdict[tuple(event_set)]] = 1.
        
        return encoder_input_data, decoder_input_data, decoder_target_data 
        
    elif mode == 3: # encoding 3
        for i, (input_trace, target_trace) in enumerate(zip(rev_X, y)):
            # ENCODER
            for t, event_set in enumerate(input_trace):
                encoder_input_data[i, t, INdict[tuple(sorted(event_set))]] = 1.
                if len(event_set) > 1: # set 1 for the subsets 
                    idxs = [INdict[tuple(sorted(subset))] for subset in all_subsets(event_set, len(event_set)-1)]
                    encoder_input_data[i, t, idxs] = 1.
            # DECODER
            for t, event_set in enumerate(target_trace):
                decoder_input_data[i, t, OUTdict[tuple(event_set)]] = 1.
                if t > 0:
                    decoder_target_data[i, t - 1, OUTdict[tuple(event_set)]] = 1.
        
        return encoder_input_data, decoder_input_data, decoder_target_data 


# time stamp functions
def remove_timezones(log):
    """ Takes the timezone offset of each timestamp and adds it to the timestamp + removes the timezone."""
    
    for trace in log:
        for event in trace:
            tz_offset = event["time:timestamp"].tzinfo.utcoffset(event["time:timestamp"])
            event["time:timestamp"] = event["time:timestamp"].replace(tzinfo=None) + tz_offset
    return log

def abstract_time(log, time_func):
    """ Abstract the specified time level (in time_func) from the timestamps of the log.
        Possible: time_func <-- abstract_{microseconds, seconds, minutes, hours, 
                                          day, month, year}.
    """
    for trace in log:
        for event in trace:
            event["time:timestamp"] = time_func(event["time:timestamp"])

def abstract_microseconds(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace(microsecond=0)

def abstract_seconds(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace(second=0, microsecond=0)

def abstract_minutes(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace(minute=0, second=0, microsecond=0)

def abstract_hours(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

def abstract_day(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def abstract_month(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

def abstract_year(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace(year=1993, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

def copy_timestamp(timestamp: datetime.datetime) -> datetime.datetime:
    return timestamp.replace()