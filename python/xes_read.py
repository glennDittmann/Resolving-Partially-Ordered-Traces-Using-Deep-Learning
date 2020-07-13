#in BPI_2012 5006 (38.3%) of the traces are uncertain       ---> assume the order in the log = correct order
#in BPI_2014 41353 (97.2%) of the traces are uncertain      ---> derive correct order from incident_acitivity_number data attribute
#in TRAFFIC_FINES 9166 (6.1%) of the traces are uncertain   ---> 
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.timestamp import timestamp_filter
import xml.etree.ElementTree as et
from pprint import pprint

#prints the specified trace of a log(certain or uncertain)
def better_print_trace_infos(log, num_trace, kind):
    if kind == "c":
        name = "Certain Trace"
    elif kind == "u":
        name = "Uncertain Trace" 
    print(name, num_trace, "has length ", len(log[num_trace]))
    log_trace_events = []
    for event in log[num_trace]:
        log_trace_events.append(event["concept:name"])
    print("And its events are:")
    print(log_trace_events, "\n")


#prints a certain trace, given by number
def print_case(log, num):
    case = log[num]
    print("\n case id: %s" % (case.attributes["concept:name"]))
    for event_index, event in enumerate(case):
        a = "event index: " + str(event_index)
        b = "event activity: " + str(event["concept:name"])
        c = "time: " + str(event["time:timestamp"])
        print('{:20s}{:60s}{:20s}'.format(a,b,c))


#prints all cases up to the given number
def print_cases(log, num_traces):
    count = 0
    for case_index, case in enumerate(log):
        print("\n case index: %d  case id: %s" % (case_index, case.attributes["concept:name"]))
        for event_index, event in enumerate(case):
            a = "event index: " + str(event_index)
            b = "event activity: " + str(event["concept:name"])
            c = "time: " + str(event["time:timestamp"])
            print('{:20s}{:60s}{:20s}'.format(a,b,c))
        count += 1
        if(count > num_traces-1):
            break
    print()


#checks if a case is certain, gets called by split traces
def case_is_certain(case_time_list):
    for i in range(0, len(case_time_list)-1):
        if case_time_list[i] == case_time_list[i+1]:
            return False
    return True


#splits a log in two logs, the one holding only totally order traces and the one holding only partially ordered traces
def split_traces(log):
    certain_traces = list()
    uncertain_traces = list()
    for case in log:
        times = list()
        for event in case:
            times.append(event["time:timestamp"])
        if case_is_certain(times):
            certain_traces.append(case)
        else:
            uncertain_traces.append(case)
    return certain_traces, uncertain_traces


#returns the average trace length for a log
def avg_trace_length(log):
    avg = 0
    for case in log:
        avg += len(case)
    return round(avg / len(log),2)


#returns the length of the longest trace in a log
def max_trace_length(log):
    max = 0
    for case in log:
        if len(case) >= max:
            max = len(case)
    return max


#returns a list of dicts, for each trace, the keys for a trace are timestamps holding all events occuring at that time for a specific trace
def make_trace_sets(log):
    trace_as_sets = []
    for i in range(0, len(log)):
        j = 0
        trace = dict()
        while j < len(log[i]):
            if str(log[i][j]["time:timestamp"]) in trace:
                trace[str(log[i][j]["time:timestamp"])].append(log[i][j]["concept:name"])
            else:
                trace[str(log[i][j]["time:timestamp"])] = [log[i][j]["concept:name"]]
            j += 1
        for key in trace:
            trace[key].sort()
        trace_as_sets.append(trace)
    return trace_as_sets


#gets the occuring uncertain sequences in the log as a set datastructure 
def get_uncertain_sequences(uncertain_log):
    uncertain_sequences = set()
    for i in range(0, len(uncertain_log)):
        j = 0
        while j < len(uncertain_log[i])-1:
            sequence = list()
            if uncertain_log[i][j]["time:timestamp"] == uncertain_log[i][j+1]["time:timestamp"]:
                time = uncertain_log[i][j]["time:timestamp"] 
                while j < len(uncertain_log[i]) and time == uncertain_log[i][j]["time:timestamp"]:
                    sequence.append(uncertain_log[i][j]["concept:name"])
                    j += 1
            else:
                j += 1    
            if sequence:
                uncertain_sequences.add(tuple(sorted(sequence)))
    return uncertain_sequences


#gets for the occuring uncertain sequences the amount of times they come up in the log, as a dict data structure
def num_uncertain_sequences(uncertain_trace_as_sets, uncertain_sequences):
    num_uncertain_sequences = dict()
    for trace in uncertain_trace_as_sets:
        for key in trace:
            if len(trace[key]) > 1:
                if tuple(trace[key]) not in num_uncertain_sequences:
                    num_uncertain_sequences[tuple(trace[key])] = 1
                else:
                    num_uncertain_sequences[tuple(trace[key])] += 1

    return num_uncertain_sequences


# set log path' as variables
SEPSIS        = "Sepsis_Cases_Event_Log.xes"    #contains   1050 traces  #number of unique events = 16    96% uncertain
PERMIT        = "PermitLog.xes"                 #contains   7065 traces  #number of unique events = 51    13% uncertain
BPI_2012      = "BPI_Challenge_2012.xes"        #contains  13087 traces  #number of unique events = 24    38% uncertain
BPI_2014      = "BPI_Challenge_2014.xes"        #contains  41353 traces  #number of unique events = 9     93% uncertain
TRAFFIC_FINES = "traffic_fines.xes"             #contains 150370 traces  #number of unique events = 11     6% uncertain

#log = xes_import_factory.import_log(SEPSIS)
log = xes_importer.apply(SEPSIS)

activities = attributes_filter.get_attribute_values(log, "concept:name")
print("--------------------------------------------------------------- \n")
print('Load log with %s traces.\n' %len(log))
print("Number of unique events = ", len(activities))
all_events = list(activities.keys())
print("Which are: \n", all_events, "\n")

certain_log, uncertain_log = split_traces(log)
NUM_TRACES = len(certain_log)+len(uncertain_log)
print("Number of certain traces: ", len(certain_log))
print("Avg trace length:", avg_trace_length(certain_log))
print("Max trace length:", max_trace_length(certain_log))
print()
print("Number of uncertain traces: ", len(uncertain_log))
print("Avg trace length:", avg_trace_length(uncertain_log))
print("Max trace length:", max_trace_length(uncertain_log))
print("Fraction of uncertain traces: ", round(len(uncertain_log)/NUM_TRACES*100,2), "% \n")


uncertain_sequences = get_uncertain_sequences(uncertain_log)
print("Uncertain Sets in the log are:")
#pprint(uncertain_sequences)
#get the uncertain / certain traces in sets of events with the same timestamps as in the papers definiton of traces
certain_traces_as_sets = make_trace_sets(certain_log)
uncertain_traces_as_sets = make_trace_sets(uncertain_log)
num_uncertain_sequences = num_uncertain_sequences(uncertain_traces_as_sets, uncertain_sequences)

pprint(num_uncertain_sequences)
print()
#pprint(uncertain_traces_as_sets[123])
#print_case(uncertain_log, 123)


#TODO: create training set of a small log (supposedly BPI_2012, and 80% of the certain traces, 
#            the rest 20% traces can be used for evalutaion; order in the log = correct order)

#TODO: think of how to map event names / datetime.datetime as NN input and what would the output be