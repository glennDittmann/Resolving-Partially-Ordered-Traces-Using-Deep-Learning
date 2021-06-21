import utils as u 
import numpy as np

class Encoder1():
  def __init__(self, activity_list, max_seq_len, repeat_unc_vec=True, enc_outputs=False):
    self.activities = activity_list
    self.n_features = len(activity_list)
    self.max_seq_len = max_seq_len
   
    # in the lstm model the uncertain vectors are repeated
    self.repeat_unc_vec = repeat_unc_vec
    self.enc_outputs = enc_outputs

    self.activity_to_idx = dict((e,i) for i,e in enumerate(self.activities))
    self.idx_to_activity = dict((i,e) for i,e in enumerate(self.activities))

  def one_hot_encode_log(self, log_set):
    enc_trace_sets = []
    for trace_set in log_set:
      enc_trace_sets.append(self.one_hot_encode_trace(trace_set))

    enc_log = np.stack(enc_trace_sets)

    return enc_log

  def one_hot_encode_trace(self, trace_set):
    enc_event_sets = [] 
    for event_set in trace_set:
        enc_event_sets.append(self.one_hot_encode_event(event_set))

    if self.repeat_unc_vec: # cant use stack here since repetition of vecs gives unequally shaped event sets
      enc_trace = np.concatenate(enc_event_sets)
    else: # cant use concatenate here cause we get (n,1) vecs as encoded event_sets and this would concatnate to n (m,1) vec with m = n * num_event_sets
      enc_trace = np.stack(enc_event_sets)

    #pad the encoded trace, such that it is of the max seq length, i.e. pad of value max_seq_sel - enc_trace.shape[0]
    if self.max_seq_len - enc_trace.shape[0] > 0:
      pad_length = self.max_seq_len - enc_trace.shape[0] # - enc_trace.shape[0]
      enc_trace = np.pad(enc_trace, ((0,pad_length),(0,0))) 

    return enc_trace

  def one_hot_encode_event(self, event_set):
    enc_event = np.zeros(self.n_features)
    indices = self.lookup_indices(event_set)
    enc_event[indices] = 1
    
    if self.repeat_unc_vec:
      enc_event = np.tile(enc_event, (len(event_set), 1))

    return enc_event

  def lookup_indices(self, event_set):
    if self.enc_outputs:
        indices = self.activity_to_idx[event_set]
    else:
        indices = [self.activity_to_idx[activity] for activity in event_set]
    return indices
    

class Encoder2():
  
  def __init__(self, activity_list, max_seq_len, sort_event_sets=True):
    self.activities = activity_list
    self.n_features = len(activity_list)
    self.max_seq_len = max_seq_len
    self.activity_to_idx = dict( (tuple(e_set),i) for i,e_set in enumerate(self.activities))    #all possible uncertain sequences to come up in traces (inputs)
    self.idx_to_activity = dict( (i,tuple(e_set)) for i,e_set in enumerate(self.activities))
    self.sort_event_sets = sort_event_sets # used for encoding unc_sets (sorted) i.e. B,D,B = B,B,D VS pos_res BDB != BBD

  def one_hot_encode_log(self, log_set):
    enc_trace_sets = []
    for trace_set in log_set:
      enc_trace_sets.append(self.one_hot_encode_trace(trace_set))

    enc_log = np.stack(enc_trace_sets)

    return enc_log

  def one_hot_encode_trace(self, trace_set):
    enc_event_sets = [] 
    for event_set in trace_set:
        enc_event_sets.append(self.one_hot_encode_event_set(event_set))
    
    enc_trace = np.stack(enc_event_sets)

    #pad the encoded trace, such that it is of the max seq length, i.e. pad of value max_seq_sel - enc_trace.shape[0]
    if self.max_seq_len - enc_trace.shape[0] > 0:
      pad_length = self.max_seq_len - enc_trace.shape[0] # - enc_trace.shape[0]
      enc_trace = np.pad(enc_trace, ((0,pad_length),(0,0))) 

    return enc_trace

  def one_hot_encode_event_set(self, event_set):
    enc_event = np.zeros(self.n_features)
    indice = self.lookup_indice(event_set)
    enc_event[indice] = 1

    return enc_event

  def lookup_indice(self, event_set):
    if self.sort_event_sets:
      return self.activity_to_idx[tuple(sorted(event_set))]
    else:
      return self.activity_to_idx[tuple(event_set)]


class Encoder3():
  def __init__(self, activity_list, max_seq_len, sort_event_sets=True):
    self.activities = activity_list
    self.n_features = len(activity_list)
    self.max_seq_len = max_seq_len
    self.activity_to_idx = dict( (tuple(e_set),i) for i,e_set in enumerate(self.activities))    #all possible uncertain sequences to come up in traces (inputs)
    self.idx_to_activity = dict( (i,tuple(e_set)) for i,e_set in enumerate(self.activities))
    self.sort_event_sets = sort_event_sets # used for encoding unc_sets (sorted) i.e. B,D,B = B,B,D VS pos_res BDB != BBD

  def one_hot_encode_log(self, log_set):
    enc_trace_sets = []
    for trace_set in log_set:
      enc_trace_sets.append(self.one_hot_encode_trace(trace_set))

    enc_log = np.stack(enc_trace_sets)

    return enc_log

  def one_hot_encode_trace(self, trace_set):
    enc_event_sets = [] 
    for event_set in trace_set:
        enc_event_sets.append(self.one_hot_encode_event_set(event_set))
    
    enc_trace = np.stack(enc_event_sets)

    #pad the encoded trace, such that it is of the max seq length, i.e. pad of value max_seq_sel - enc_trace.shape[0]
    if self.max_seq_len - enc_trace.shape[0] > 0:
      pad_length = self.max_seq_len - enc_trace.shape[0] # - enc_trace.shape[0]
      enc_trace = np.pad(enc_trace, ((0,pad_length),(0,0))) 

    return enc_trace

  def one_hot_encode_event_set(self, event_set):
    enc_event = np.zeros(self.n_features)
    indice = self.lookup_indice(event_set)
    enc_event[indice] = 1

    if self.sort_event_sets and len(event_set) > 1:
      subsets = u.all_subsets(event_set, len(event_set)-1)
      extra_indices = [self.lookup_indice(subset) for subset in subsets] 
      enc_event[extra_indices] = 1

    return enc_event

  def lookup_indice(self, event_set):
    if self.sort_event_sets:
      return self.activity_to_idx[tuple(sorted(event_set))]
    else:
      return self.activity_to_idx[tuple(event_set)]
