# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 15:58:04 2013

@author: hlampesberger
"""

import itertools
import collections
import os
import subprocess
import tempfile


__all__ = ['Result', 'epsilon', 'empty_set', 'state_generator', 'mapping']

epsilon = ""
empty_set = set()

# enum workaround
class Result(object):
    reject, accept, neutral = range(3)

def state_generator(formatter=lambda x: x):
    for i in itertools.count(start=0):
        yield formatter(i)

def mapping(formatter=lambda x: x):
    gen = state_generator(formatter)
    return collections.defaultdict(lambda: next(gen)).__getitem__


class TransitionError(Exception):
    pass



def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def write_img(automaton, path, imgtype, exclude_labels, exclude_states):
    (fd, filename) = tempfile.mkstemp()
    try:
        tfile = os.fdopen(fd, "w")
        automaton.write_graphviz(tfile, exclude_labels, exclude_states)
        tfile.close()
        dot = which("dot")
        if dot is None:
            if os.name == "nt":
                dot = "dot"
            else:
                # OSX workaround
                dot = "/opt/local/bin/dot"        
        subprocess.call([dot, "-T%s" % imgtype, "-o",
                         '.'.join((str(path), imgtype)), filename], shell=True)
    finally:
        os.remove(filename)

def write_pdf(auto, name="test", exclude_labels=False, exclude_states=None):
    write_img(auto, name, "pdf", exclude_labels, exclude_states)

def write_png(auto, name="test", exclude_labels=False, exclude_states=None):
    write_img(auto, name, "png", exclude_labels, exclude_states)
