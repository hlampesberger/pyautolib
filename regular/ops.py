# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 15:52:57 2013

@author: hlampesberger
"""

from base import epsilon, state_generator
from operator import itemgetter


import collections


def write_graphviz(fsa, fd, exclude_labels=False, exclude_states=None):
    # header
    fd.write("digraph G {\n")
    fd.write("  rankdir=LR;\n")
    id_gen = state_generator()
    state_id = collections.defaultdict(lambda: next(id_gen))

    # content
    for s in fsa.states:
        if (exclude_states is None) or (s not in exclude_states):
            sid = state_id[s]
            if s in fsa.accept:
                fd.write("  n%d [label=\"%s\",shape=\"doublecircle\"];\n" % (sid, s))
            elif s in fsa.reject:
                fd.write("  n%d [label=\"%s\",shape=\"circle\"];\n" % (sid, s))
            else:
                fd.write("  n%d [label=\"%s\",shape=\"circle\",style=\"filled\"];\n" % (sid, s))

    # dummy start
    if isinstance(fsa.start, set):
        for s in fsa.start:
            sid = state_id[s]
            fd.write("  START%d [shape=\"point\",color=\"white\",fontcolor=\"white\"];\n" % sid)
            fd.write("  START%d -> n%d;\n" % (sid, sid))
    else:
        sid = state_id[fsa.start]
        fd.write("  START%d [shape=\"point\",color=\"white\",fontcolor=\"white\"];\n" % sid)
        fd.write("  START%d -> n%d;\n" % (sid, sid))

    # edges between nodes
    # first collect all labels for one edge
    store = collections.defaultdict(lambda: [])
    for s, sym, ns in fsa.itertransitions():
        if (exclude_states is None) or \
        (s not in exclude_states and ns not in exclude_states):
            if sym == epsilon:
                store[s, ns].append("&#949;")   #greek epsilon
            else:
                store[s, ns].append(sym)
    # then write it
    for k, v in store.items():
        sid = state_id[k[0]]
        nsid = state_id[k[1]]
        if exclude_labels:
            fd.write("  n%d -> n%d;\n" % (sid, nsid))
        else:
            fd.write("  n%d -> n%d [label=\"%s\"];\n" % (sid, nsid,
                                                 ','.join(sorted(map(str,v)))))
    # trailer        
    fd.write("}\n")


def promote(dfa, red, blue, state, order, update_order=True):
    red.add(state)
    blue.discard(state)
    if update_order:
        if not order:
            order["red"] = {state: 0}
            order["blue"] = {}
        else:
            order["red"][state] = order["blue"][state]
            del(order["blue"][state])
    #succ = { ns for sp in dfa.delta.values() for ns in sp.successors(state) }
    succ = dfa.successor(state)
    update_set = succ - red
    if update_order:
        for b in update_set:
            order["blue"][b] = order["red"][state] + 1
    blue.update(update_set)
    return red, blue, order



def merge(dfa, red_state, blue_state):
    # merge blue into red recursively
    if dfa.transitions is None:
        raise RuntimeError("Merging states requires pure transitions")
    for a in dfa.alphabet:
        #pred = { s for s in dfa.delta[a].predecessors(blue_state) }
        #pred = dfa.predecessor(blue_state)
        for s in dfa.states:
            if dfa.delta(s, a) == blue_state:
                #del(dfa.transitions[s, a])
                dfa.transitions[s, a] = red_state
            #dfa.delta[a][s, blue_state] = False
            #dfa.delta[a][s, red_state] = True
    return _fold(dfa, red_state, blue_state)



def _fold(dfa, q_dest, q_root):
    queue = collections.deque()
    queue.append((q_dest, q_root)) 
    while queue:
        q_dest, q_root = queue.popleft()
        if q_root in dfa.accept:
            dfa.accept.add(q_dest)
        for a in dfa.alphabet:
            #q_root_next = dfa.delta[a].det_transition(q_root)
            #q_dest_next = dfa.delta[a].det_transition(q_dest)
            q_root_next = dfa.delta(q_root, a)
            q_dest_next = dfa.delta(q_dest, a)
            if q_root_next is not None:
                if q_dest_next is not None:
                    queue.append((q_dest_next, q_root_next))
                else:
                    dfa.transitions[q_dest, a] = q_root_next
    dfa._complete = None
    return dfa


def choose(blue, order):
    #print sorted(order["blue"].items(), key=itemgetter(1))
    tmp = sorted(order["blue"].items(), key=itemgetter(1))[0]
    return tmp[0]  

        
