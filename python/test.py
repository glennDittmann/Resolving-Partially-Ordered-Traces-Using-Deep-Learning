import pprint
from math import comb
from xes_read import *
from encoding import *


SEPSIS        = "Sepsis_Cases_Event_Log.xes"    #contains   1050 traces  #number of unique events = 16    96% uncertain
PERMIT        = "PermitLog.xes"                 #contains   7065 traces  #number of unique events = 51    13% uncertain
BPI_2012      = "BPI_Challenge_2012.xes"        #contains  13087 traces  #number of unique events = 24    38% uncertain
BPI_2014      = "BPI_Challenge_2014.xes"        #contains  41353 traces  #number of unique events = 9     93% uncertain
TRAFFIC_FINES = "traffic_fines.xes"             #contains 150370 traces  #number of unique events = 11     6% uncertain


log = load_log(SEPSIS)
all_events = get_events_sorted(log)             #list of all events, i.e. the set of all possible events, ordered alphabetically
NUM_EVENTS = len(all_events)
certain_log, uncertain_log = split_log(log)
print("Length of: Log:", len(log), "Certain Log:", len(certain_log), "Uncertain Log:", len(uncertain_log))
print("Number of unique events:", len(all_events))

encoder = log_encoder(all_events, 2, embedding_dim=2)
test_trace = get_trace(log, 1049)
test_trace_list = get_traces(log)
e_test_trace = encoder.embed_encode_trace(test_trace)
print(all_events)
print(test_trace)
print(e_test_trace)
#############################################################################
print(len(test_trace_list))
print(test_trace_list[1049])
encoded_inputs = []
for trace in test_trace_list:
    encoded_inputs.append(encoder.embed_encode_trace(trace))
print(encoded_inputs[1049])