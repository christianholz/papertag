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

if 'edit' in form:
    edit = form.getvalue('edit')
else:
    print '''error: edit parameter'''
    sys.exit(-1)
edit = os.path.split(edit)[1].lower()
if not edit in [v[0].lower() for v in config['edit']] or os.path.splitext(edit)[1].lower() == '.py':
    print '''error: edit file not found'''
    sys.exit(-1)
edit = [v[0].lower() for v in config['edit']].index(edit)
ed_tp = config['edit'][edit]


print '''<!DOCTYPE html>
<html>
<head>
<title>edit %s</title>
<link href="style.css" rel="stylesheet" />
</head>
<body>
<nav><a href="list.py?user=%s">&lt; list</a></nav>''' % (ed_tp[1], user)

if 'submit' in form.keys():
    msg = tagdb.save_file(ed_tp[0], form.getvalue('config_raw'))
    if msg == None:
        print '''<div class="msg">%s updated</div>''' % (ed_tp[1])
    else:
        print '''<div class="emsg">%s</div>''' % (msg)

ls = tagdb.load_file_raw(ed_tp[0])
print '''<h1>Edit %s</h1>
<form action="config.py?user=%s&edit=%s" method="post">
<textarea name="config_raw" id="config_raw">'''% (ed_tp[1], user, ed_tp[0])
print "".join(ls)
print '''</textarea>
<input type="submit" id="submit" name="submit" value="update %s" onclick="javascript:return confirm('overwrite %s?');"/>
</form>
</body>''' % (ed_tp[1], ed_tp[1])
