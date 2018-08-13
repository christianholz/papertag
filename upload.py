#!/usr/bin/env python

import os
import sys
import cgi
import json
import tagdb
import cgi
import cgitb; cgitb.enable()
import md5
try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass

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


papers = tagdb.parse_bibtex()
paper  = None
for item in papers:
    if item['pid'] == pid:
        paper = item
        break
if paper == None:
    print '''error: paper not found'''
    sys.exit(-1)

if 'file-upload' in form:
    # Generator to buffer file chunks
    def fbuffer(f, chunk_size=10000):
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            yield chunk

    # A nested FieldStorage instance holds the file
    fileitem = form['file']

    # Test if the file was uploaded
    if fileitem.filename:
        if os.path.splitext(fileitem.filename)[1] != '.pdf':
            message = 'Only PDF files allowed'
            cssClass = 'upload-error'
        else:
            # strip leading path from file name to avoid directory traversal attacks
            fn = os.path.basename(fileitem.filename)
            f = open('files/' + md5.md5(pid).hexdigest() + '.pdf', 'wb', 10000)

            # Read the file in chunks
            for chunk in fbuffer(fileitem.file):
              f.write(chunk)
            f.close()
            message = 'The file "' + fn + '" was uploaded successfully'
            cssClass = 'upload-success'

    else:
        message = 'No file was uploaded'
        cssClass = 'upload-error'

    print """\
    <p class="upload-result %s">%s</p>
    """ % (cssClass, message)
else:
    print 'no direct access'
