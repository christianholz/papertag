#!/usr/bin/env python

import os
import sys
import cgi
import json
import tagdb
import datetime


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
if 'sort' in form:
    sort = form.getvalue('sort')
else:
    sort = 'title'

papers = tagdb.parse_bibtex()
msg = ""

if 'init' in form and int(form.getvalue('init')) > 0:
    tagdb.init_assignment(user, int(form.getvalue('init')))
    msg = "papers reset and reassigned"

view_cb = []
for j, cb in enumerate(config['done']):
    if done == j:
        view_cb.append('%s and up' % (cb))
    else:
        view_cb.append('<a href="?user=%s&filter=%s&done=%d">%s%s</a>' % (user, int(filtered), j, cb, " and up" * (j != len(config['done']) - 1)))

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
<nav>%s | view progress: %s<div style="float:right">%s | <form method="post" name="reinit" action="?user=%s" style="display:inline"><input type="hidden" name="init" value="1"><a href="#" onclick="javascript:if(confirm('(re)initialize assignments?'))document.forms['reinit'].submit();return false;">initialize assignments</a></form></div></nav>
''' % (sm, ' | '.join(view_cb), edit_cb, user)

if msg != "":
    print '''<div class="msg">%s</div>''' % (msg)

print '''<h1>All papers</h1>
<table>
<tr>
    <th class="exp"><a href="?user=%s&filter=%d&done=%d&sort=title">title</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=doi">doi</a></th>
    <th class="nexp">action</th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=3">assigned</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=5">last change</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=4">last user</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=7">progress</a></th>
</tr>''' % (user, int(filtered), done, user, int(filtered), done, user, int(filtered), done,
            user, int(filtered), done, user, int(filtered), done, user, int(filtered), done)

def nice_dt(d):
    if d.days >= 500:
        return "never"
    if d.days >= 7:
        return str(d.days / 7) + " week" + "s" * (d.days >= 14)
    if d.days >= 1:
        return str(d.days) + " day" + "s" * (d.days >= 2)
    if d.seconds >= 60 * 60:
        return str(d.seconds / 60 / 60) + " hour" + "s" * (d.seconds >= 60 * 60)
    if d.seconds >= 60:
        return str(d.seconds / 60) + " minute" + "s" * (d.seconds >= 120)
    return "now"
    
now = datetime.datetime.utcnow()
render = []
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
        render.append([item, unf, bgc, m[0], m[1], m[2], nice_dt(now - m[2]), config['done'][m[3]]])

if len(sort) == 1:
    render.sort(key=lambda x:x[int(sort)])
else:
    render.sort(key=lambda x:x[0][sort])
for r in render:
    print '''<tr>
    <td class="exp">%s</td>
    <td class="nexp"%s><a href="https://dx.doi.org/%s">link</a></td>
    <td class="nexp"%s><a href="edit.py?user=%s&pid=%s">edit</a></td>
    <td class="nexp"%s%s>%s</td>
    <td class="nexp"%s>%s</td>
    <td class="nexp"%s>%s</td>
    <td class="nexp"%s>%s</td>
</tr>''' % (r[0]['title'], r[1], r[0]['doi'], r[1], user, r[0]['pid'], r[2], r[1], r[3], r[1], r[6], r[1], r[4], r[1], r[7])

if len(render) == 0:
    print '''<tr>
    <td class="exp" style="font-style:italic;text-align:center">no papers to show</td>
    <td class="nexp"></td>
    <td class="nexp"></td>
    <td class="nexp"></td>
    <td class="nexp"></td>
    <td class="nexp"></td>
    <td class="nexp"></td>
</tr>'''

print '''
</table>
</body>
</html>'''
