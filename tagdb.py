#!/usr/bin/env python

import os
import sys
import json
import md5
import time
import datetime
import bibtexparser


# path_prefix = ''
path_prefix = 'cgi-bin/'

extra_fields = ['pid_assigned', 'pid_user', 'pid_access', 'pid_done', 'pid_ago']
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
        j = json.load(f)
    except:
        ag = datetime.datetime.utcnow() - datetime.datetime(2000, 1, 1)
        return ['', '', datetime.datetime(2000, 1, 1), 1, ag.days * 24 * 60 * 60 + ag.seconds]
    f.close()
    j['pid_access'] = datetime.datetime.fromtimestamp(j['pid_access'])
    d = datetime.datetime.utcnow() - j['pid_access']
    j['pid_ago'] = d.days * 24 * 60 * 60 + d.seconds
    j['pid_done'] = int(j['pid_done'])
    j = [j.get(v, '') for v in extra_fields]
    return j


def load_config():
    global tagdb_config
    tagdb_config = json.load(open(path_prefix + 'config.json'))
    return tagdb_config


def check_unique(recs, field, recursive=-1, keys=[], dupl=[]):
    for r in recs:
        if r[field] in keys:
            dupl.append(r[field])
        else:
            keys.append(r[field])
        if recursive >= 0:
            check_unique(r[recursive], field, recursive, keys, dupl)
    return dupl
            

def save_file(fname, raw):
    global tagdb_config
    fc = os.path.split(fname)[-1]
    fc = os.path.splitext(fc)
    if not fname in [v[0].lower() for v in tagdb_config['edit']] or fc[1].lower() == '.py':
        return "file not in edit list"
    if fc[1] == '.json':
        try:
            t = json.loads(raw)
        except ValueError as e:
            return e.message
        except:
            return "JSON parsing exception"
        if fc[0] == 'config':
            dupl = check_unique(t['fields'], 0, 4)
            if len(dupl):
                return "duplicate key%s: " % ("s" * (len(dupl) != 1)) + ", ".join(dupl) + "<br/>"
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
        j = json.load(f)
    except:
        return {}
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

