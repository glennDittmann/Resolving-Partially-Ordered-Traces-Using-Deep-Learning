#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 16:35:24 2020

@author: glenn
"""
from itertools import product, permutations, combinations, combinations_with_replacement
import tensorflow as tf

test=['a','b','c','d']
for i in range(1, len(test)+1):
    print(list(combinations(test,i)))

activities = ['|a|', '|b|', '|c|', '|a|a|', '|a|b|', '|a|c|', '|b|b|', '|b|a|', '|b|c|', '|c|c|', '|c|a|', '|c|b|', 
              '|a|a|a|', '|a|a|b|', '|a|a|c|', '|a|b|a|', '|a|b|b|', '|a|b|c|', '|a|c|a|', '|a|c|b|', '|a|c|c|', 
              '|b|a|a|', '|b|a|b|', '|b|a|c|', '|b|b|a|', '|b|b|b|', '|b|b|c|', '|b|c|a|', '|b|c|b|', '|b|c|c|', 
              '|c|a|a|', '|c|a|b|', '|c|a|c|', '|c|b|a|', '|c|b|b|', '|c|b|c|', '|c|c|a|', '|c|c|b|', '|c|c|c|']
indices = tf.range(len(activities), dtype=tf.int64)

tf.print(indices)

table_init = tf.lookup.KeyValueTensorInitializer(activities, indices)

table = tf.lookup.StaticVocabularyTable(table_init, 1)


#itertools product method (for getting all possible combinations of events of a certain length) returns a list of tuples which needs to be converted into a list of strings/events
def itertools_tuples_to_list(tupleList: list, k: int):
  result = []
  for tup in tupleList:
    possibleResolution = '|'
    for i in range(0,k):
      possibleResolution += tup[i].lstrip('|')
    if possibleResolution not in result: #or len(tup) == 1:
      result.append(possibleResolution)
  return result

def all_possible_resolutions(singular_events: list, k: int):
  really_all_possible_resolutions = []
  for i in range(1,k+1):
    really_all_possible_resolutions += itertools_tuples_to_list( list(permutations(singular_events, i)), i)
    
  return really_all_possible_resolutions

c = ['|a|', '|b|', '|c|']
all_subsets= []
for i in range(1,len(c)+1):
    all_subsets += itertools_tuples_to_list( list(combinations(c, i)), i)
print(all_subsets)      
d = all_possible_resolutions(c, 3)
print(d)

def all_subsequences(event_set, separizer: str='|'):
    event_set = event_set[1:-1]
    single_events = ['|' + x + '|' for x in event_set.split('|')]
    all_subsequences = all_possible_resolutions(single_events, len(single_events))
    return all_subsequences
    

#mimicking encoder class 
es = '|a|b|c|d|'                          
length = len([x for x in es.split('|')])-2
print(length)
res = [es] + ['|' + single_event + '|' for single_event in es[1:-1].split('|')]
for i in range(2,length):                                   #get all subsets of length >=2 for the current possible resolution
    left, right = '|'+es.split('|',i)[i], es.rsplit('|',i)[0]+'|'
    if left not in res:
        res.append(left)
    if right not in res:
        res.append(right)
print(res)
test = all_subsequences(event_set)
print(test)
categories = tf.constant(test)
tf.print(categories)

cat_indices = table.lookup(categories)

tf.print(cat_indices)

cat_one_hot = tf.one_hot(cat_indices, depth=len(activities) + 1)
type(cat_one_hot)
liste = [t for t in tf.one_hot(cat_indices, depth=len(activities) + 1)]
fin = tf.math.add_n(liste)
tf.print(fin)

#------------------get all subsequences for trace ----------------------------#
test = '|a|b|c|d|'

def all_subsequs(test):
    length = len([x for x in test.split('|')])-2
    if length == 1:
        return [test]
    else:
        res = [test] + ['|' + e + '|' for e in test[1:-1].split('|')]
        for i in range(2,length):
            res.append('|'+test.split('|',i)[i])
            res.append(test.rsplit('|',i)[0]+'|') 
        return res
print(all_subsequs(test))


e_set = '|a|a|b|c|'
def all_subsets(event_set):
    length = len([x for x in event_set.split('|')])-2
    if length == 1:
        return [event_set]
    else:
        singles = ['|' + e + '|' for e in event_set[1:-1].split('|')]
        subsets = []
        for i in range(1,len(singles)+1):
            combis = itertools_tuples_to_list(list(combinations(singles, i)), i)
            for combi in combis:
                if combi not in subsets:
                    subsets.append(combi)
    subsets.sort(key=len)
    return subsets
print(all_subsets(e_set))