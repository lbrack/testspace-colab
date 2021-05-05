import json
import os

def get_file_name(dir, project):
    return dir + "{}.json".format(project.replace(":", "_"))

def rd_details_cases(fname):
    f = open(fname, "r")
    return(json.load(f))

def wr_details_cases(details, dir, fname):

    if not os.path.exists(dir):
        os.makedirs(dir)
    file_name= dir + "{}.json".format(fname.replace(":", "_"))
    f = open(file_name, "w")
    fdata = json.dumps(details,indent=4, sort_keys=True)
    f.write(fdata)
    return

#################################################################
# TBD.
#################################################################

def track(status, state, track):
  
    newstate = "NONE"
    newtrack = 0
    if status == "passed" and state == "NONE":
        return newstate, newtrack

    ###########################################
    # FAILED
    ###########################################    
    if status == "failed":

        if state == "NONE":
            newstate = "NEW"
            newtrack = 1
        elif state == "NEW":
            newstate = "CONSISTENT"
            newtrack = 2
        elif state == "CONSISTENT":
            newstate = "CONSISTENT"
            newtrack = track+1
        elif state == "FLAKY":
            if track == 4:
                newstate = "CONSISTENT"
                newtrack = 5
            else:
                newstate = "FLAKY"
                newtrack = track+1
        elif state == "PASSING":
            newstate = "FLAKY"
            newtrack = 1

    ###########################################
    # PASSED
    ###########################################    
    elif status == "passed":
        
        if state == "NEW":
            newstate = "PASSING"
            newtrack = 2
        elif state == "CONSISTENT":
            newstate = "PASSING"
            newtrack = 1
        elif state == "FLAKY":
            if track == 4:
                newstate = "RESOLVED"
                newtrack = 5
            else:
                newstate = "FLAKY"
                newtrack = track+1
        elif state == "PASSING":
            if track == 4:
                newstate = "RESOLVED"
                newtrack = 5
            else:
                newstate = "PASSING"
                newtrack = track+1
            
    return newstate, newtrack

##############################################################
#
# MultiIndexed framy by passing a tuples dictionary
# https://pandas.pydata.org/docs/user_guide/dsintro.html#from-a-dict-of-tuples 
#
###############################################################

status = {"passed": 1, "failed": 0}

def convert_to_tuples_dict(casesDict, prevResultItem):
    tuplesDict = {}
    
    for case in casesDict:
        # The "flatting" of Result content also can contain non-case info    
        if 'status' in case:      
            tuplesDict[(case['name'], 'status')]   = status[case['status']]
            tuplesDict[(case['name'], 'duration')] = float(case['duration'])
            tuplesDict[(case['name'], 'path')]     = case['path']
            if not prevResultItem:
                newstate, newtrack = track(case['status'], 'NONE', 0)
                tuplesDict[(case['name'], 'state')]  = newstate
                tuplesDict[(case['name'], 'track')]  = newtrack
            elif (case['name'], 'status') in prevResultItem:
                newstate, newtrack = track(case['status'], prevResultItem[(case['name'], 'state')], prevResultItem[(case['name'], 'track')])
                tuplesDict[(case['name'], 'state')]  = newstate
                tuplesDict[(case['name'], 'track')]  = newtrack
            else:
                tuplesDict[(case['name'], 'state')]  = 'NONE'
                tuplesDict[(case['name'], 'track')]  = 0
               
    return tuplesDict

def convert_to_tuples_dict_summary(summaryTable):
    tuplesDict = {}

    for case in summaryTable:
        tuplesDict[(case['case'], 'count')]    = case['count']
        tuplesDict[(case['case'], 'pr')]       = case['pr']
        tuplesDict[(case['case'], 'time')]     = case['time']
        tuplesDict[(case['case'], 'history')]  = case['history']

    return tuplesDict


    