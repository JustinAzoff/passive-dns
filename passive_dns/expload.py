#!/usr/bin/env python
import sys

from passive_dns.client import SearchClient, show
c = SearchClient()



def expload(qs, seen=None):
    if seen is None:
        seen = set()
    seen.update(qs)
    new = []
    
    for q in qs:
        q_results = c.search_question(" " + q)
        a_results = c.search_answer(q + " ")
        results = q_results + a_results
        for x in results:
            show(x)

            if x['key'] not in seen:
                new.append(x['key'])
            if x['value'] not in seen:
                new.append(x['value'])

    if new:
        expload(new, seen)

def main():
    qs = sys.argv[1:]
    expload(qs)

if __name__ == "__main__":
    main()
