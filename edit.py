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

if 'pid' in form:
    pid = form.getvalue('pid')
else:
    print '''error: paper not set'''
    sys.exit(-1)

if 'submit' in form:
    # they really have the oldest Py2 installation
    dt = {}
    for k in form.keys():
        if k != 'submit' and k != 'user':
            dt[k] = form.getvalue(k)
    tagdb.save_paper(dt['pid'], dt, user)
    msg = '''<div class="msg">Paper saved</div>'''
else:
    msg = ''


papers = tagdb.parse_bibtex()
paper  = None
for item in papers:
    if item['pid'] == pid:
        paper = item
        break
if paper == None:
    print '''error: paper not found'''
    sys.exit(-1)

print '''<!DOCTYPE html>
<html>
<head>
<title>Edit %s</title>
<link href="style.css" rel="stylesheet" />
</head>
<body>
<nav><a href="list.py?user=%s">&lt; list</a></nav>
%s
<h1>%s</h1>
<a href="https://dx.doi.org/%s">doi link</a>
<form action="edit.py?user=%s&pid=%s" method="post">
<table>
<tr>
    <th class="nexp">field</th>
    <th class="exp">value</th>
    <th class="taglinks">default values</th>
</tr>''' % (paper['title'], user, msg, paper['title'], paper['doi'], user, pid)

pdata = tagdb.load_paper(pid)

def gen_field(st, indent=0):
    for s in st:
        # ["contrib", "Main contribution", "line", [], []],
        if s[2] == 'line':
            ed = '<input type="text" name="%s" id="%s" value="%s"/>' % (s[0], s[0], pdata.get(s[0], ''))
        elif s[2] == 'box':
            ed = '<textarea name="%s" id="%s">%s</textarea>' % (s[0], s[0], pdata.get(s[0], ''))
        else:
            ed = ''
        dv = []
        for v in s[3]:
            dv.append('<a href="#" onclick="javascript:document.getElementById(\'%s\').value=\'%s\';return false;">%s</a>' % (s[0], v, v))
        print '''<tr>
    <td class="nexp" style="padding-left:%dpx">%s</td>
    <td class="exp">%s</td>
    <td class="taglinks">%s</td>
</tr>''' % (indent * 20, s[1], ed, ' '.join(dv))

        if len(s[4]):
            gen_field(s[4], indent + 1)

print '''<tr>
    <td class="nexp">Bibtex raw</td>
    <td class="exp"><textarea id="bibtex" disabled="disabled" style="font-family:monospace;font-size:10pt;white-space:pre;background-color:#eee">%s</textarea></td>
    <td class="taglinks"></td>
</tr>''' % (''.join(paper['bibtex']))

gen_field(config['fields'])
gen_field([['pid_assigned', "Assigned to", 'line', config['users'], []]])

if 'pid_done' in pdata:
    done = int(pdata['pid_done'])
else:
    done = 1

view_cb = []
for j, cb in enumerate(config['done']):
    if done == j:
        view_cb.append('<input type="radio" name="pid_done" id="pid_done_%d" value="%d" checked="checked"/><label for="pid_done_%s">%s</label>' % (j, j, j, cb))
    else:
        view_cb.append('<input type="radio" name="pid_done" id="pid_done_%d" value="%d"><label for="pid_done_%s">%s</label>' % (j, j, j, cb))


print '''<tr>
    <td>done</td>
    <td>%s</td>
    <td></td>
</tr>
</table>
<input type="submit" id="submit" name="submit" value="submit tags"/>
</form>
</body>
</html>
''' % (''.join(view_cb))
