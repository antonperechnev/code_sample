#!/usr/bin/env python3
#import cgitb
import sqlite3 as sq
import os
import json
import sys
import re
#print("Content-type: text/html\n")
print("Content-type: application/json\n\n")
#con = sq.connect('test.db')#попробовал добавить путь до базы в cgi-bin
if os.environ['REQUEST_METHOD'] == 'GET':
    id = re.findall('(\d+)', os.getenv('QUERY_STRING'))[0]
    con = sq.connect('test.db')
    with con:
        cur = con.cursor()
        cur.execute('SELECT * FROM NODES WHERE parent=(?)', id)
        da = cur.fetchall()
        dic = {}
        for i in da:
            dic[id] = i
        print(json.dumps(dic))
elif os.environ['REQUEST_METHOD'] == 'POST':
    dat = sys.stdin.read(int(os.environ.get('CONTENT_LENGTH', 0))) #нужно знать сколько читать данных
    data = json.loads(dat)
    con = sq.connect('test.db')
    with con:
        cur = con.cursor()
        try:
            cur.execute('INSERT INTO NODES(LABEL, PARENT) VALUES(?,?)', (data['label'], int(data['parent'])))
            con.commit()
            print(json.dumps({'code': 'OK'}))
        except:#нехорошо,но я пока не придумал как сделать
            print(json.dumps({'code': 'Already exist'}))
elif os.environ['REQUEST_METHOD'] == 'PUT':
    dat = sys.stdin.read(int(os.environ.get('CONTENT_LENGTH', 0)))
    data = json.loads(dat)
    con = sq.connect('test.db')
    with con:
        cur = con.cursor()
        cur.execute(
            'UPDATE NODES SET LABEL = (?), PARENT = (?) WHERE LABEL = (?) ',
            (data['label'], int(data['parent']), data['old_label'])
        )
        con.commit()
    print(json.dumps({"code": "OK"}))
elif os.environ['REQUEST_METHOD'] == 'DELETE':
    dat = sys.stdin.read(int(os.environ.get('CONTENT_LENGTH', 0)))
    data = json.loads(dat)
    con = sq.connect('test.db')
    with con:
        cur = con.cursor()
        cur.execute(
            'DELETE FROM NODES WHERE LABEL = (?)', (data['label'])
        )
    con.commit()
    print(json.dumps({"code": "OK"}))
