def make_hash(line):
    parts = line.split()
    key, value, type, ttl, datefirst,timefirst, datelast,timelast = parts

    first = datefirst + ' ' + timefirst
    last  = datelast  + ' ' + timelast

    return  {'key': key, 'value': value, 'type': type, 'ttl': ttl, 'first': first, 'last': last}
