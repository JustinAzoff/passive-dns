#!/usr/bin/env python
import sys

from passive_dns.client import SearchClient, show
c = SearchClient()



def expload(qs):
    seen = set()
    todo = qs
    while todo:
        new = []
        for q in todo:
            q_results = c.search_question(" " + q)
            a_results = c.search_answer(q + " ")
            results = q_results + a_results
            for x in results:
                k = x['key']
                v = x['value']
                if k not in seen or v not in seen:
                    yield x
                    if k not in seen:
                        new.append(k)
                        seen.add(k)
                    if v not in seen:
                        new.append(v)
                        seen.add(v)
        #filter akamai, otherwise this goes on forever
        new = [x for x in new if not x.endswith("akamai.net")]
        todo = new
        if new:
            yield {"new": new}

def main():
    qs = sys.argv[1:]
    for x in expload(qs):
        if 'new' in x:
            print "new:", ' '.join(x['new'])
            print
        else :
            show(x)
if __name__ == "__main__":
    main()
