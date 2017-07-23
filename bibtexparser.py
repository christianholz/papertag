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
        if bc == 0 and ls[j][0] == '@':
            title = ''
            for i in range(j, len(ls)):
                bc += ls[i].count('{')
                bc -= ls[i].count('}')
                if bc == 0:
                    pid = ls[j].split('{')[1].strip(', \r\n')
                    items.append([pid, title, ls[j:i+1]])
                    break
                l = ls[i].strip(' ,')
                if l.startswith('title'):
                    e = l.index('=')
                    title = l[e+1:].strip(' {},\r\n')
            j = i + 1
        j += 1
    return items


def duplicate(items):
    keys = []
    for it in items:
        if it[0] in keys:
            return it[0]
        keys.append(it[0])
    return None

