import xlrd
import xml.dom.minidom
import sqlite3

'''
tools/input.py

实现功能：
1. 以文件形式批量导入数据，存放到表history

使用说明：
1. 实例化类input_history,调用xml_import(file_path)
2. 实例化类input_history,调用excel_import(file_path)

注意事项：
1. 默认需要文件：
    knowledge.db

2. xml导入文件格式：
<root>
	<knowledge>
		<question>问句</question>
		<answer>答案</answer>
	</knowledge>
	<knowledge>
		<question>问句</question>
		<answer>答案</answer>
	</knowledge>
</root>

3. excel导入问句格式：
--------sheet 1:--------------
-- A  |  B
1 问句 | 答案
2 问句 | 答案

'''


class input_history(object):
    def xml_import(self, file_path):
        dom = xml.dom.minidom.parse(file_path)
        root = dom.documentElement
        knowledge = root.getElementsByTagName('knowledge')
        dict = {}
        for i in knowledge:
            question = i.getElementsByTagName('question')[0]
            answer = i.getElementsByTagName('answer')[0]
            dict[question.childNodes[0].data] = answer.childNodes[0].data
        self.import2db(dict)

    def excel_import(self, file_path):
        table = xlrd.open_workbook(file_path).sheets()[0]
        dict = {}
        for i in range(table.nrows):
            dict[table.cell(i, 0).value] = table.cell(i, 1).value
        self.import2db(dict)

    def import2db(self, dict):
        print(dict)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS [history]')
        c.execute('CREATE TABLE history(id INTEGER PRIMARY KEY AUTOINCREMENT,question TEXT NOT NULL,answer TEXT NOT NULL)')
        for i in dict:
            c.execute('INSERT INTO history (question, answer) VALUES (?, ?);', (i, dict.get(i)))
        conn.commit()
        conn.close()

    def __init__(self):
        self.db_path =  'knowledge.db'

if __name__ == '__main__':
    a = input_history()
    a.xml_import('a.xml')
