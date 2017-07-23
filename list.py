#!/usr/bin/env python

import os
import sys
import cgi
import json
import tagdb


print "Content-type: text/html\r\n"


config = tagdb.load_config()
form = cgi.FieldStorage()
user = tagdb.auth(form)
if not user:
    print '''error: user'''
    sys.exit(-1)

if 'done' in form:
    done = int(form.getvalue('done'))
else:
    done = 1

filtered = 'filter' in form and int(form.getvalue('filter'))


papers = tagdb.parse_bibtex()

view_cb = []
for j, cb in enumerate(config['done']):
    if done == j:
        view_cb.append('%s and up' % (cb))
    else:
        view_cb.append('<a href="?user=%s&filter=%s&done=%d">%s and up</a>' % (user, int(filtered), j, cb))

if filtered:
    sm = '<a href="?user=%s&done=%d">view all papers</a>' % (user, done)
else:
    sm = '<a href="?user=%s&filter=1&done=%s">view papers assigned to me</a>' % (user, done)

edit_cb = []
for j, cb in enumerate(config['edit']):
    edit_cb.append('<a href="config.py?user=%s&edit=%s">%s</a>' % (user, cb[0], cb[1]))
if len(edit_cb):
    edit_cb = "edit: " + ' | '.join(edit_cb)
else:
    edit_cb = ""

print '''<!DOCTYPE html>
<html>
<head>
<title>Paper tag list</title>
<link href="style.css" rel="stylesheet" />
</head>
<body>
<nav>%s | %s<div style="float:right">view progress: %s</div></nav>
<h1>All papers</h1>
<table>
<tr>
    <th class="exp">title</th>
    <th class="nexp">doi</th>
    <th class="nexp">action</th>
    <th class="nexp">assigned</th>
    <th class="nexp">last change</th>
    <th class="nexp">last user</th>
    <th class="nexp">progress</th>
</tr>
''' % (sm, edit_cb, ' | '.join(view_cb))

cnt = 0
for item in papers:
    m = tagdb.get_meta(item['pid'])
    if (not filtered or m[0] == user) and (m[3] >= done):
        if m[0] == '':
            bgc = ' style="background-color:#fcc"'
        else:
            bgc = ''
        if m[0] == user:
            unf = ' style="background-color:#aaa"'
        else:
            unf = ''
        cnt += 1
        print '''<tr>
        <td class="exp">%s</td>
        <td class="nexp"%s><a href="https://dx.doi.org/%s">link</a></td>
        <td class="nexp"%s><a href="edit.py?user=%s&pid=%s">edit</a></td>
        <td class="nexp"%s%s>%s</td>
        <td class="nexp"%s>%s</td>
        <td class="nexp"%s>%s</td>
        <td class="nexp"%s>%s</td>
    </tr>''' % (item['title'], unf, item['doi'], unf, user, item['pid'], bgc, unf, m[0], unf, m[2], unf, m[1], unf, config['done'][m[3]])

if cnt == 0:
    print '''<tr>
    <td class="exp" style="font-style:italic;text-align:center">no papers to show</td>
    <td class="nexp"></td>
    <td class="nexp"></td>
    <td class="nexp"></td>
    <td class="nexp"></td>
    <td class="nexp"></td>
</tr>'''

print '''
</table>
</body>
</html>
'''
