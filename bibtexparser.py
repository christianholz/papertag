#!/usr/bin/env python


def parse_file(name):
    f = open(name)
    ls = f.readlines()
    return parse_lines(ls)


def parse_lines(ls):
    items = []
    bc = 0
    j = 0
    while j < len(ls):
        if bc == 0 and len(ls[j]) and ls[j][0] == '@':
            title = ''
            doi = ''
            for i in range(j, len(ls)):
                bc += ls[i].count('{')
                bc -= ls[i].count('}')
                if bc == 0:
                    pid = ls[j].split('{')[1].strip(', \r\n')
                    items.append({
                        'pid': pid,
                        'title': title,
                        'doi': doi,
                        'bibtex': ls[j:i+1]
                    })
                    break
                l = ls[i].strip(' ,')
                if l.startswith('title'):
                    e = l.index('=')
                    title = l[e+1:].strip(' {},\r\n')
                if l.startswith('doi'):
                    e = l.index('=')
                    doi = l[e+1:].strip(' {},\r\n')
            j = i + 1
        j += 1
    return items


def duplicate(items):
    keys = []
    for it in items:
        if it['pid'] in keys:
            return it['pid']
        keys.append(it['pid'])
    return None

