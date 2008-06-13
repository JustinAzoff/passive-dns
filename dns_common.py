import os
LOC="/var/captures/dns/"

answer_dir = os.path.join(LOC, "by_answer")
query_dir  = os.path.join(LOC, "by_query")

def make_hash(line):
    parts = line.split()
    if len(parts)==8:
        key, value, type, ttl, datefirst,timefirst, datelast,timelast = parts
    else:
        type = 'A'
        key, value, ttl, datefirst,timefirst, datelast,timelast = parts

    first = datefirst + ' ' + timefirst
    last  = datelast  + ' ' + timelast

    #temp
    value = value.lower()
    key = key.lower()
    if value.endswith("."):
        value=value[:-1]

    return  {'key': key, 'value': value, 'type': type, 'ttl': ttl, 'first': first, 'last': last}
