from pm4py.objects.log.importer.xes import importer as xes_importer

sepsis_log = xes_importer.apply("logs/Sepsis_Cases_Event_Log.xes")
print("DONE!")
#create the three algorithms from the prior paper


#TODO maybe make an abstract class "probabilistic model"


class FullTraceEquivalenceProbabilisticModel():
    
    def __init__(self, certain_log):
        self.certain_log = certain_log
        self.len_certain_log = len(certain_log)
        self.trace_frequency = dict()
        
        self.__get_trace_frequencies()

    def __get_trace_frequencies(self):
        for trace in self.certain_log:
            self.trace_frequency[trace] = self.trace_frequency.get(trace, 0) + 1


    def P_trace(self, possible_resolution) -> float:
        return self.trace_frequency.get(possible_resolution, 0) / self.len_certain_log


class NGramProbabilisticModel():

    def __init__(self, log):
        self.log = log
        self.log_set = self.__make_log_set()

        self.certain_sequences = [self.__make_certain_sequences(trace_set) for trace_set in log_set]

    def certain(self, activity_sequence: list, trace_set: dict) -> bool:
        certain_sequences = self.__make_certain_sequences(trace_set)
        for certain_sequence in certain_sequences:
            if __activities_in_sequence(activity_sequence, certain_sequence):
                return True
        return False

    def __make_log_set(self) -> list:
        log_set = []
        for trace in self.log:
            log_set.append(self.__make_trace_sets(trace))
        return log_set

    def __make_trace_sets(self, trace) -> dict:
        trace_set = dict()
        for event in trace:
            trace_set[str(event["time:timestamp"])] = trace_set.get(str(event["time:timestamp"]), []) + [event["concept:name"]]
        return trace_set

    def __make_certain_sequences(self, trace_set) -> list:
        '''
        For each uncertain trace we cut out the certain subtraces, e.g. [{1}, {2,3}, {4}, {5}] -> [[1],[4,5]]
        And in those we search for an activity sequence to be present
        Because for an activity sequence to be certain in a trace it must apper in a certain sequence of a trace
        '''
        certain_sequences = []
        certain_sequence = []
        for i, timestamp in enumerate(trace_set):
          if len(trace_set[timestamp]) == 1:
            if i == len(trace_set)-1:
              certain_sequence.append(trace_set[timestamp][0])
              certain_sequences.append(certain_sequence)
            else:
              certain_sequence.append(trace_set[timestamp][0])
          else:
            if certain_sequence:
              certain_sequences.append(certain_sequence)
            certain_sequence = []
        return certain_sequences 

    def __activities_in_sequence(self, activity_sequence: list, certain_sequence: list) -> bool:
        for i in range(len(certain_sequence) - len(activity_sequence) + 1):
            if certain_sequence[i:i+len(activity_sequence)] == activity_sequence:
                return True
        return False

    def P_a_activity_sequence(self, activity: str, activity_sequence: list) -> float:
        cnt1 = 0
        cnt2 = 0
        for trace_set in self.log_set:
            if certain(activity_sequence, trace_set):
                cnt2 += 1
            if certain(activity_sequence + [activity], trace_set):
                cnt1 += 1
        if cnt2 == 0: 
          return cnt1
        return cnt1/cnt2

    def P_n_gram(self, possible_resolution: list, n: int=2):
        #possible_resolution like [a, b, c]
        lower_bound = 1         #2 in the paper, but indexing here starts one before
        upper_bound = len(possible_resolution)
        result = 1.0
        for i in range(lower_bound,upper_bound):
            s_index = max(i-n+1, 0)         #the gram is not n long in the beginning, its 2 long, then 3, ... until it's always n long
            result *= self.P_a_activitiy_sequence(possible_resolution[i], s_index)
        return result


class BinaryRelationsProbabilisticModel():

    def __init__(self, log):
        self.log = log
        self.log_set = self.__make_log_set()

    def order(self, a: str, b: str, trace_set) -> bool:
        trace_list = [event_set for timestamp, event_set in trace_set.items()]
        for i in range(len(trace_list)-1):
            if a in trace_list[i]:
                for j in range(i+1, len(trace_list)):
                    if b in trace_list[j]:
                        return True
        return False

    def contains_activities(self, a: str, b: str, trace_set):
        activities = [event for timestamp, event_set in log_set[6].items() for event in event_set]
        return (a in activities and b in activities)

    def __make_log_set(self) -> list:
        log_set = []
        for trace in self.log:
            log_set.append(self.__make_trace_sets(trace))
        return log_set

    def __make_trace_sets(self, trace) -> dict:
        trace_set = dict()
        for event in trace:
            trace_set[str(event["time:timestamp"])] = trace_set.get(str(event["time:timestamp"]), []) + [event["concept:name"]]
        return trace_set

    def P_a_b(self, a:str, b:str) -> float:
        cnt1 = 0
        cnt2 = 0
        for trace_set in self.log_set:
            if contains_activities(a, b, trace_set):
                cnt2 += 1
                if order(a, b, trace_set):
                    cnt1 += 1
        if cnt2 == 0:
            return cnt1
        return cnt1 / cnt2

    def P_weak_order(self, possible_resolution: list) -> float:
        result = 1.0
        for i in range(len(possible_resolution)-1):
            for j in range(i+1, len(possible_resolution)):
                result *= self.P_a_b(possible_resolution[i], possible_resolution[j])
        return result
