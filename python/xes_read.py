#in BPI_2012 5006 (38.3%) of the traces are uncertain       ---> assume the order in the log = correct order
#in BPI_2014 41353 (97.2%) of the traces are uncertain      ---> derive correct order from incident_acitivity_number data attribute
#in TRAFFIC_FINES 9166 (6.1%) of the traces are uncertain   ---> 
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.timestamp import timestamp_filter
import xml.etree.ElementTree as et
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.rc('xtick', labelsize=8)
import numpy as np
from pathlib import Path

def visualize_log():
    color_log, color_certain, color_uncertain = 'tab:blue', 'darkseagreen', 'sandybrown'
    #visualize basic log information

    fig, ax = plt.subplots(1,2)
    #certain and uncertain log length as pie chart
    def func(pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}%\n({:d} Traces)".format(pct, absolute)

    labels = ['Certain Part', 'Uncertain Part']
    sizes = [len(certain_log)/NUM_TRACES*100, len(uncertain_log)/NUM_TRACES*100]
    wedges, texts, autotexts = ax[0].pie(sizes, startangle=90, colors = [color_certain, color_uncertain], 

                                            autopct=lambda pct: func(pct, [len(certain_log), len(uncertain_log)]), textprops=dict(color="k"))
    ax[0].set_title('Traces of the Log that are Certain, Uncertain Respectively')

    #measures for trace length
    X1 = ['avg', 'min', 'max', 'c_avg', 'c_min', 'c_max', 'u_avg', 'u_min', 'u_max'] 
    y1 = [log_avg, log_min, log_max, certain_avg, certain_min, certain_max, uncertain_avg, uncertain_min, uncertain_max]
    r2 = ax[1].bar(X1, y1, color=[color_log, color_log, color_log, color_certain, color_certain, color_certain, color_uncertain, color_uncertain, color_uncertain])
    ax[1].set_title('Trace Length Measures in the whole, certain and uncertain Log')
    ax[1].set_ylabel('Number of Events')

    #frequency of each even in the log
    fig1, ax1 = plt.subplots(3,1)
    ax1[0].bar(range(len(frequency_of_events_log)), frequency_of_events_log.values(), align='center')
    ax1[0].set_title('Log')
    ax1[0].set_ylabel('Amount of Occurance')
    ax1[1].bar(range(len(frequency_of_events_certain)), frequency_of_events_certain.values(), align='center')
    ax1[1].set_title('Certain Log')
    ax1[1].set_ylabel('Amount of Occurance')
    ax1[2].bar(range(len(frequency_of_events_uncertain)), frequency_of_events_uncertain.values(), align='center')
    ax1[2].set_title('Uncertain Log')
    ax1[2].set_ylabel('Amount of Occurance')
    fig1.suptitle('Frequency of Events in the whole, certain and uncertain log', fontsize=20)
    plt.setp(ax1, xticks=[i for i in range(len(all_events))], xticklabels = list(frequency_of_events_log.keys()))

    # visualize uncertain trace frequency
    X = list()
    y = list()
    for key in num_uncertain_sequences:
        s = ''
        for event in key:
            s += event[:2]
        X.append(s)
        y.append(num_uncertain_sequences[key])

    fig2, ax2 = plt.subplots()    
    ax2.bar(X,y)
    ax2.set_title('Uncertain Set Frequency')
    ax2.set_xlabel('Uncertain Trace Set')
    ax2.set_ylabel('Frequency in the Log')


    plt.show()

#loads log from a given .xes file, specified with the filename (file must lay on same level as function calling script)
def load_log(filename):
    path_to_logs = Path('../logs').resolve()
    log = xes_importer.apply(str(path_to_logs) + '/' + filename)
    return log

#gets a list of the unique events as strings, sorted alphabetically
def get_events_sorted(log):
    activities = attributes_filter.get_attribute_values(log, "concept:name")
    all_events = list(activities.keys())
    all_events.sort()
    return all_events

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
def split_log(log):
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

#returns the amount of events in the log
def num_events(log):
    num_events = 0 
    for case in log:
        num_events += len(case)
    return num_events

#retruns a list of the events from a particular trace from the log
def get_trace(log, trace_index):
    if trace_index > len(log)-1:
        print("Trace index out of range")
    else:
        trace = [event["concept:name"] for event in log[trace_index]]
        return trace

#returns a list of lists, each containing the events from the traces of the given log
def get_traces(log):
    trace_list = list()
    for case in log: 
        trace_list.append([ event["concept:name"] for event in case ])
            
    return trace_list

#returns the average trace length for a log
def avg_trace_length(log):
    avg = 0
    for case in log:
        avg += len(case)
    return round(avg / len(log),2)


#returns the length of the shortest trace in a log
def min_trace_length(log):
    min = 10000
    for case in log:
        if len(case) < min:
            min = len(case)
    return min

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


def frequency_of_events(all_events, log):
    frequency_of_events = dict()
    for event in all_events:
        frequency_of_events[event] = 0
    for case in log:
        for event in case:
            frequency_of_events[event["concept:name"]] += 1

    return frequency_of_events

# set log path' as variables
""" SEPSIS        = "Sepsis_Cases_Event_Log.xes"    #contains   1050 traces  #number of unique events = 16    96% uncertain
                                                #num of uncertain event sets: 3079 #number of uncertain events:
PERMIT        = "PermitLog.xes"                 #contains   7065 traces  #number of unique events = 51    13% uncertain
BPI_2012      = "BPI_Challenge_2012.xes"        #contains  13087 traces  #number of unique events = 24    38% uncertain
BPI_2014      = "BPI_Challenge_2014.xes"        #contains  41353 traces  #number of unique events = 9     93% uncertain
TRAFFIC_FINES = "traffic_fines.xes"             #contains 150370 traces  #number of unique events = 11     6% uncertain

log = load_log(SEPSIS)
all_events = get_events_sorted(log)
NUM_TRACES = len(log)
certain_log, uncertain_log = split_log(log)

frequency_of_events_log = frequency_of_events(all_events, log)
frequency_of_events_certain = frequency_of_events(all_events, certain_log)
frequency_of_events_uncertain = frequency_of_events(all_events, uncertain_log)

log_avg, log_min, log_max = avg_trace_length(log), min_trace_length(log), max_trace_length(log)
certain_avg, certain_min, certain_max = avg_trace_length(certain_log), min_trace_length(certain_log), max_trace_length(certain_log)
uncertain_avg, uncertain_min, uncertain_max = avg_trace_length(uncertain_log), min_trace_length(uncertain_log), max_trace_length(uncertain_log)

uncertain_sequences = get_uncertain_sequences(uncertain_log)
certain_traces_as_sets = make_trace_sets(certain_log)
uncertain_traces_as_sets = make_trace_sets(uncertain_log)
num_uncertain_sequences = num_uncertain_sequences(uncertain_traces_as_sets, uncertain_sequences)

print("------------------------------------------------------------------------------------------------------------------- \n")
print("Number of traces: ", len(log))
print("Avg trace length:", log_avg)
print("Min trace length:", log_min)
print("Max trace length:", log_max)
print()
print("Number of certain traces: ", len(certain_log))
print("Avg trace length:", certain_avg)
print("Min trace length:", certain_min)
print("Max trace length:", certain_max)
print()
print("Number of uncertain traces: ", len(uncertain_log))
print("Avg trace length:", uncertain_avg)
print("Min trace length:", uncertain_min)
print("Max trace length:", uncertain_max)
print("Fraction of uncertain traces: ", round(len(uncertain_log)/NUM_TRACES*100,2), "% \n")
print("Number of unique events = ", len(all_events))
print("Which are: \n", all_events, "\n")

print("Uncertain Sets in the log are (with", len(num_uncertain_sequences),"kinds of uncertain sets):")
total_number = 0
for key in num_uncertain_sequences:
    total_number += num_uncertain_sequences[key]
print("The total number of uncertain event sets appearing in the log is:", total_number)
pprint(num_uncertain_sequences)
b = {2:0,3:0,4:0}
for key in num_uncertain_sequences:
    b[len(key)] += 1
pprint(b)
print()
pprint(uncertain_traces_as_sets[10])
print_case(uncertain_log, 10)
 """
#visualize data of log
#visualize_log()


#TODO: create training set of a small log (supposedly BPI_2012, and 80% of the certain traces, 
#            the rest 20% traces can be used for evalutaion; order in the log = correct order)

#TODO: think of how to map event names / datetime.datetime as NN input and what would the output be

#TODO:
        #make the second chart align avg, min and max bars
        #make a color legend for the first figure
        #set colors for frequency of events 
        #set colormap for higher values for frequency of events and frequency of uncertain sets
        #write numbers over the bars 