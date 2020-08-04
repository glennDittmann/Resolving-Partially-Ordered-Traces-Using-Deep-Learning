import pprint
from xes_read import *

SEPSIS        = "Sepsis_Cases_Event_Log.xes"    #contains   1050 traces  #number of unique events = 16    96% uncertain
PERMIT        = "PermitLog.xes"                 #contains   7065 traces  #number of unique events = 51    13% uncertain
BPI_2012      = "BPI_Challenge_2012.xes"        #contains  13087 traces  #number of unique events = 24    38% uncertain
BPI_2014      = "BPI_Challenge_2014.xes"        #contains  41353 traces  #number of unique events = 9     93% uncertain
TRAFFIC_FINES = "traffic_fines.xes"             #contains 150370 traces  #number of unique events = 11     6% uncertain

input1 = [['u'],['v','w','x'],['y','z']]
output2 = 'uvwxy'

input2 = [['u','v'],['x'],['y','z']]

log = load_log(SEPSIS)
all_events = get_events_sorted(log)
pprint(all_events)
certain_log, uncertain_log = split_log(log)
print(len(log), len(uncertain_log), len(certain_log))
