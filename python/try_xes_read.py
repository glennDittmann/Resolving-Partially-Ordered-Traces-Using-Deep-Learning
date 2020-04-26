from pm4py.objects.log.importer.xes import factory as xes_import_factory
import xml.etree.ElementTree as et
from pprint import pprint

TRAFFIC_FINES = "traffic_fines.xes"       #contains 150370 traces
BPI_2012      = "BPI_Challenge_2012.xes"  #contains  13087 traces

log = xes_import_factory.apply(BPI_2012)
print('Load log with %s traces.' %len(log))
pprint(log[0])

count = 0
for case_index, case in enumerate(log):
    print("\n case index: %d  case id: %s" % (case_index, case.attributes["concept:name"]))
    for event_index, event in enumerate(case):
        #print("event index: %d  event activity: %s %70s" % (event_index, event["concept:name"], "time: " + str(event["time:timestamp"])))
        a = "event index: " + str(event_index)
        b = "event activity: " + str(event["concept:name"])
        c = "time: " + str(event["time:timestamp"])
        print('{:20s}{:55s}{:20s}'.format(a,b,c))
    count += 1
    if(count > 20):
        break



#does not work with traffic_fines
def load_xes(file, event_filter = []):
    log = []
    
    tree = et.parse(file)
    data = tree.getroot()
    
    # find all traces
    traces = data.findall('{http://www.xes-standard.org/}trace')
    
    for t in traces:
        trace_id = None
        
        # get trace id
        for a in t.findall('{http://www.xes-standard.org/}string'):
            if a.attrib['key'] == 'concept:name':
                trace_id = a.attrib['value']
        
        events = []
        # events
        for event in t.iter('{http://www.xes-standard.org/}event'):
            
            e = {'name': None, 'timestamp': None, 'resource': None, 'transition': None}
            
            for a in event:
                e[a.attrib['key'].split(':')[1]] = a.attrib['value']
            
            if e['name'] in event_filter or len(event_filter) == 0:
                events.append(e)
        
        # add trace to log
        if len(events) > 0:
            log.append({'trace_id': trace_id, 'events': events})
        
    return log

#log = load_xes(BPI_2012)
#print('Load log with %s traces.' %len(log))
#pprint(log[:3])