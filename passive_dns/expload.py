#!/usr/bin/env python
import sys

from passive_dns.client import SearchClient, show
c = SearchClient()



def expload(qs):
    seen = set()
    todo = qs
    while todo:
        new = []
        seen.update(todo)
        for q in todo:
            q_results = c.search_question(" " + q)
            a_results = c.search_answer(q + " ")
            results = q_results + a_results
            for x in results:
                yield x

                if x['key'] not in seen:
                    new.append(x['key'])
                if x['value'] not in seen:
                    new.append(x['value'])
        todo = new
        if new:
            yield {"new": new}

def main():
    qs = sys.argv[1:]
    for x in expload(qs):
        if 'new' in x:
            print "\nnew:", ' '.join(x['new'])
        else :
            show(x)

if __name__ == "__main__":
    main()
