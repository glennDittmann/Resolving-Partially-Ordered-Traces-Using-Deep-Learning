import pprint
from xes_read import *
from encoding import *

SEPSIS        = "Sepsis_Cases_Event_Log.xes"    #contains   1050 traces  #number of unique events = 16    96% uncertain
PERMIT        = "PermitLog.xes"                 #contains   7065 traces  #number of unique events = 51    13% uncertain
BPI_2012      = "BPI_Challenge_2012.xes"        #contains  13087 traces  #number of unique events = 24    38% uncertain
                                                #assume the correct order is the order in the log
BPI_2014      = "BPI_Challenge_2014.xes"        #contains  41353 traces  #number of unique events = 9     93% uncertain
                                                #correct order derivable from incidents ativity (could be equal log order)
TRAFFIC_FINES = "traffic_fines.xes"             #contains 150370 traces  #number of unique events = 11     6% uncertain


log = load_log(SEPSIS)
all_singular_events = get_events(log)             #list of all events, i.e. the set of all possible events, ordered alphabetically
certain_log, uncertain_log = split_log(log)

# getting the possible events ready, i.e. the elements of the lookup table for encoding
uncertain_events = get_uncertain_sequences(uncertain_log)           #all occuring uncertain sequences as tuples
list_uncertain_events = make_list_uncertain_sequences(uncertain_events) #all occuring sequences in a list, concatenated
all_events = all_singular_events + list_uncertain_events

#getting the traces in a form such that the event sequences match the lookup table for encoding, i.e. trace = list of (concatenated) event-strings
#data structure: a log is list of dicts(=traces), where the key is the timestamp and it contains all single events happening at that time
log_sets = make_set_log(log)
certain_log_sets = make_set_log(certain_log)
uncertain_log_sets = make_set_log(uncertain_log)

#data structure: a logg is a list of lists(=traces), where each event is represented as a string, those who had the same timestamps in a trace are concatenated
concatenated_log = concatenate_trace_sets(log_sets)
concatenated_certain_log = concatenate_trace_sets(certain_log_sets)
concatenated_uncertain_log = concatenate_trace_sets(uncertain_log_sets)

# encoding the input log
encoder = log_encoder(all_singular_events, 1)
encoded_inputs = encoder.one_hot_encode_log(concatenated_certain_log)


#printing some valuable information for veryfing things work
print("Length of: Log:", len(log), "Certain Log:", len(certain_log), "Uncertain Log:", len(uncertain_log))
print("Number of singular events:", len(all_singular_events), "Number of possible input events:", len(all_events))
print(all_events)
pprint(concatenated_certain_log[17])
pprint(encoded_inputs[17])
pprint(certain_log_sets[17])

#for assuming the correct order is as in the log and only using the certain log
encoded_targets = encoder.one_hot_encode_log(concatenated_certain_log) #it's the same as the encoded input in this case