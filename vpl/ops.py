# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 10:43:22 2013

@author: hlampesberger
"""

from base import epsilon, state_generator
import collections

__all__ = ['write_graphviz']


def write_graphviz(vpa, fd, exclude_labels=False,
                               exclude_states=None):
    # header
    fd.write("digraph G {\n")
    fd.write("  rankdir=LR;\n")
    id_gen = state_generator()
    state_id = collections.defaultdict(lambda: next(id_gen))

    # content
    for s in vpa.states:
        if (exclude_states is None) or (s not in exclude_states):
            sid = state_id[s]
            if s in vpa.accept:
                fd.write("  n%d [label=\"%s\",shape=\"doublecircle\"];\n" % (sid, s))
            else:
                fd.write("  n%d [label=\"%s\",shape=\"circle\"];\n" % (sid, s))
            #else:
            #    f.write("  n%d [label=\"%s\",shape=\"circle\",style=\"filled\"];\n" % (sid, s))

    # dummy start
    if isinstance(vpa.start, set):
        for s in vpa.start:
            sid = state_id[s]
            fd.write("  START%d [shape=\"point\",color=\"white\",fontcolor=\"white\"];\n" % sid)
            fd.write("  START%d -> n%d;\n" % (sid, sid))
    else:
        sid = state_id[vpa.start]
        fd.write("  START%d [shape=\"point\",color=\"white\",fontcolor=\"white\"];\n" % sid)
        fd.write("  START%d -> n%d;\n" % (sid, sid))

    # edges between nodes
    # first collect all labels for one edge
    store = collections.defaultdict(lambda: [])
    for s, sym, ns in vpa.iterinterns():
        if (exclude_states is None) or \
        (s not in exclude_states and ns not in exclude_states):
            if sym == epsilon:
                store[s, ns].append("&#949;")   #greek epsilon
            else:
                store[s, ns].append(sym)
    for q, a, qn, gamma in vpa.itercalls():
        if (exclude_states is None) or \
        (q not in exclude_states and qn not in exclude_states):
            if a == epsilon:
                store[q, qn].append("&#949;/%s" % str(gamma))   #greek epsilon
            else:
                store[q, qn].append("%s/%s" % (str(a), str(gamma)))    
    for q, gamma, a, qn in vpa.iterreturns():
        if (exclude_states is None) or \
        (q not in exclude_states and qn not in exclude_states):
            if a == epsilon:
                store[q, qn].append("&#172;&#949;/%s" % str(gamma))   #greek epsilon
            else:
                store[q, qn].append("&#172;%s/%s" % (str(a), str(gamma)))   

    # then write it
    for k, v in store.items():
        sid = state_id[k[0]]
        nsid = state_id[k[1]]
        if exclude_labels:
            fd.write("  n%d -> n%d;\n" % (sid, nsid))
        else:
            fd.write("  n%d -> n%d [label=\"%s\"];\n" % (sid, nsid,
                    ', '.join(sorted(map(str,v), reverse=True))))
    # trailer        
    fd.write("}\n")




