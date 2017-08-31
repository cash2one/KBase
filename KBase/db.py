import os, sqlite3
from flask import Flask
import requests
import time

app = Flask(__name__)

import sqlite3
from flask import g
from contextlib import closing

# 移除已有的文件，以免对测试造成干扰
DATABASE = os.path.join(os.path.dirname(__file__), 'knowledge.db')
# if os.path.isfile(DATABASE):
#     os.remove(DATABASE)

def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def get_connection():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = connect_db()
    return db

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv
#
# # 初始数据:
# conn = sqlite3.connect(db_file)
# cursor = conn.cursor()
# cursor.execute('create table kwyword(id varchar(10) primary key, keyword varchar(20), importance int, type varchar(10))')
# cursor.close()
# conn.commit()
# conn.close()

# def init_db():
#     with app.app_context():
#         db = get_db()
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

    params1 = '/keyword'
    re = http_get(params1)
    keywordlist = re['keywordlist']
    data1 = [(i['id'], i['keyword'], i['importance'], i['type']) for i in keywordlist]

    params2 = '/knowledge'
    re = http_get(params2)
    knowledgelist = re['knowledgelist']
    data2 = [(i['id'], i['qa_md5'], i['question'], i['answer'], i['link']) for i in knowledgelist]

    with closing(connect_db()) as db:
        start = time.clock()
        cursor = db.cursor()
        cursor.executemany("insert into keyword values(?, ?, ?, ?)", data1)
        cursor.executemany("insert into knowledge values(?, ?, ?, ?, ?)", data2)
        db.commit()
        cursor.close()
        db.close()
        end = time.clock()
        print (start, end, end - start)


def http_get(params):
    url = 'http://119.23.237.255/aimanage' + params
    response = requests.get(url)
    return response.json()

init_db()