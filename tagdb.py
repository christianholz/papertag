#!/usr/bin/env python

import os
import sys
import json
import md5
import time
import datetime
import bibtexparser


path_prefix = ''
# path_prefix = 'cgi-bin/'

extra_fields = ['pid_assigned', 'pid_user', 'pid_access', 'pid_done']
tagdb_config = None


def fcopy(fn, tn):
    f = open(tn, 'w')
    for l in open(fn):
        f.write(l)
    f.close()
    

def parse_bibtex():
    return bibtexparser.parse_file(path_prefix + 'all.bib')


def get_meta(pid):
    try:
        f = open(path_prefix + 'tags/' + md5.md5(pid).hexdigest() + '.json')
    except IOError:
        return ['', '', datetime.datetime(2000, 1, 1), 1]
    j = json.load(f)
    f.close()
    j['pid_access'] = datetime.datetime.fromtimestamp(j['pid_access'])
    j['pid_done'] = int(j['pid_done'])
    j = [j.get(v, '') for v in extra_fields]
    return j


def load_config():
    global tagdb_config
    tagdb_config = json.load(open(path_prefix + 'config.json'))
    return tagdb_config


def save_file(fname, raw):
    global tagdb_config
    fc = os.path.splitext(fname)
    if not fname in [v[0].lower() for v in tagdb_config['edit']] or fc[1].lower() == '.py':
        return "file not in edit list"
    if fc[1] == '.json':
        t = json.loads(raw)
    if fc[1] == '.bib':
        b = bibtexparser.parse_lines(raw.split('\n'))
        d = bibtexparser.duplicate(b)
        if len(d[0]) or len(d[1]):
            s = ""
            if len(d[0]):
                s += "duplicate key%s: " % ("s" * (len(d[0]) != 1)) + ", ".join([v[0] for v in d[0]]) + "<br/>"
            if len(d[1]):
                s += "duplicate title%s: " % ("s" * (len(d[0]) != 1)) + ", ".join([v[1] for v in d[1]]) + "<br/>"
            return s
    fcopy(path_prefix + fname, path_prefix + 'backup/' + fc[0] + '-' + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S") + fc[1])
    open(path_prefix + fname, 'w').write(raw)


def load_file_raw(fname):
    if not fname in [v[0].lower() for v in tagdb_config['edit']] or os.path.splitext(fname)[1].lower() == '.py':
        return []
    else:
        return open(path_prefix + fname).readlines()


def load_paper(pid):
    try:
        f = open(path_prefix + 'tags/' + md5.md5(pid).hexdigest() + '.json')
    except IOError:
        return {}
    j = json.load(f)
    f.close()
    return j


def save_paper(pid, data, user):
    data['pid_access'] = time.mktime(datetime.datetime.utcnow().timetuple())
    data['pid_user'] = user
    f = open(path_prefix + 'tags/' + md5.md5(pid).hexdigest() + '.json', 'w')
    json.dump(data, f)
    f.close()


def auth(form):
    if tagdb_config == None:
        load_config()
    if 'user' in form:
        user = form.getvalue('user')
    else:
        return False
    if user not in tagdb_config['users']:
        return False
    return user


def init_assignment(user, offset=0):
    if tagdb_config == None:
        load_config()
    b = parse_bibtex()
    for j, p in enumerate(b):
        d = load_paper(p['pid'])
        d['pid_done'] = 1
        d['pid_assigned'] = tagdb_config['users'][(j + offset) % len(tagdb_config['users'])]
        save_paper(p['pid'], d, user)

