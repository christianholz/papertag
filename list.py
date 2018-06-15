#!/usr/bin/env python

import os
import sys
import cgi
import json
import tagdb
import datetime
import urllib


config = tagdb.load_config()
form = cgi.FieldStorage()
user = tagdb.auth(form)
if not user:
    print '''error: user'''
    sys.exit(-1)


if 'createzip' in form and int(form.getvalue('createzip')) > 0:
    filename = tagdb.createzip(user)
    print "Status: 303 See other"
    print "Location: %s" % (filename)
    print #empty line to indicate end of header

#content type declaration after the potential redirect
print "Content-type: text/html\r\n"

if 'done' in form:
    done = int(form.getvalue('done'))
else:
    done = -1

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

if filtered:
    sm = '<a href="?user=%s&done=%d">view all papers</a>' % (user, done)
else:
    sm = '<a href="?user=%s&filter=1&done=%s">view papers assigned to me</a>' % (user, done)

if done < 0:
    view_cb = ['all']
else:
    view_cb = ['<a href="?user=%s&filter=%d&done=-1">all</a>' % (user, filtered)]
for j, cb in enumerate(config['done']):
    if done == j:
        view_cb.append(cb)
    else:
        view_cb.append('<a href="?user=%s&filter=%d&done=%d">%s</a>' % (user, filtered, j, cb))

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
<nav>%s | view progress: %s<div style="float:right">%s 
| <form method="post" name="reinit" action="?user=%s" style="display:inline"><input type="hidden" name="init" value="1"><a href="#" onclick="javascript:if(confirm('(re)initialize assignments?'))document.forms['reinit'].submit();return false;">initialize assignments</a></form> 
| <form method="post" name="download" action="?user=%s" style="display:inline"><input type="hidden" name="createzip" value="1"><a href="#" onclick="javascript:if(confirm('Re-create zip and download?'))document.forms['download'].submit();return false;">Download tags</a></form></div></nav>
''' % (sm, ' | '.join(view_cb), edit_cb, user, user )

if msg != "":
    print '''<div class="msg">%s</div>''' % (msg)


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
mecnt = 0;
auth_stat = {}
for item in papers:
    m = tagdb.get_meta(item['pid'])
    if not m[0] in auth_stat:
        auth_stat[m[0]] = [0] * len(config['done'])
    auth_stat[m[0]][m[3]] += 1
    if (filtered == 0 or m[0] == user) and (m[3] == done or done < 0):
        if m[0] == '':
            bgc = ' style="background-color:#fcc"'
        else:
            bgc = ''
        if m[0] == user:
            unf = ' style="background-color:#aaa"'
            mecnt += 1
        else:
            unf = ''
        render.append([item, unf, bgc, m[0], m[1], m[2], nice_dt(now - m[2]), config['done'][m[3]], m[4]])

if done < 0:
    assigned = '''%d papers in total''' % (len(render))
else:
    assigned = '''%d <em>%s</em> papers assigned to %s (%d total papers)''' % (mecnt, config['done'][done], user, len(render))

print '''<h1>All papers</h1>
<div class="info">%s</div><br/>
<table>
<tr>
    <th class="exp"><a href="?user=%s&filter=%d&done=%d&sort=title">title</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=doi">doi</a></th>
    <th class="nexp">scholar</th>
    <th class="nexp">action</th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=3">assigned</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=8">last change</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=4">last user</a></th>
    <th class="nexp"><a href="?user=%s&filter=%d&done=%d&sort=7">progress</a></th>
</tr>''' % (assigned,
            user, filtered, done, user, filtered, done, user, filtered, done,
            user, filtered, done, user, filtered, done, user, filtered, done)

    
if len(sort) == 1:
    render.sort(key=lambda x:x[int(sort)])
else:
    render.sort(key=lambda x:x[0][sort])
for r in render:
    scholar = urllib.quote(r[0]['title'] + ' ' + r[0]['doi'])
    print '''<tr>
    <td class="exp">%s</td>
    <td class="nexp"%s><a href="https://dx.doi.org/%s">link</a></td>
    <td class="nexp"%s><a href="https://scholar.google.com/scholar?hl=en&q=%s&btnG=">scholar</a></td>
    <td class="nexp"%s><a href="edit.py?user=%s&pid=%s">edit</a></td>
    <td class="nexp"%s%s>%s</td>
    <td class="nexp"%s>%s</td>
    <td class="nexp"%s>%s</td>
    <td class="nexp"%s>%s</td>
</tr>''' % (r[0]['title'], r[1], r[0]['doi'], r[1], scholar, r[1], user, r[0]['pid'], r[2], r[1], r[3], r[1], r[6], r[1], r[4], r[1], r[7])

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
<br/><br/>
<h1>Summary</h1>
<table id="summary">
  <tr><th class="summary_left"></th>''' + ''.join(['<th>%s</th>' % s for s in config['done']]) + '''<th>touched</th><th>total</th></tr>'''
for un in sorted(auth_stat.keys(), key=lambda x:sum(auth_stat[x]) - auth_stat[x][1], reverse=True):
    print '  <tr><td class="summary_left">%s</td>' % un + ''.join(['<td>%d</td>' % i for i in auth_stat[un]]) + '<td>%d</td><td>%d</td></tr>' % (sum(auth_stat[un]) - auth_stat[un][1], sum(auth_stat[un]))
print '''</table>
</body>
</html>'''
