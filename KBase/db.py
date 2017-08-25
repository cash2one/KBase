import os, sqlite3

# 移除已有的文件，以免对测试造成干扰
db_file = os.path.join(os.path.dirname(__file__), 'knowledge.db')
if os.path.isfile(db_file):
    os.remove(db_file)

# 初始数据:
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute('drop table if exites [keyword]')
cursor.execute('create table kwyword(id varchar(10) primary key, keyword varchar(20), importance int, type varchar(10)')
cursor.close()
conn.commit()
conn.close()