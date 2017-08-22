import json
import sqlite3

'''
init_cut.py

实现功能：
1. 批量导入到history中的问题进行初始分词，存入数据库keyword、extend表

使用说明：
1. 实例化类ini_cut，调用方法update_history()实现

注意事项：
1. 默认需要文件：
    dict/jieba.dict
    dict/keyword.dict
    dict/stopwords.dict
    
    a.json
    
    knowledge.db
'''


class init_cut:
    def load_dict(self):
        # 读取keyword词典
        dict_keyword = {}
        with open('dict/keyword.dict', encoding='utf8') as f:
            for line in f:
                (val, type, imp) = line.strip().split(',')
                dict_keyword[val] = type
        # 读取jieba词典
        dict_jieba = {}
        with open('dict/jieba.dict', encoding='utf8') as f:
            for line in f:
                (val, fre, type) = line.strip().split(' ')
                dict_jieba[val] = type
        # 读取stopword列表
        list_stopword = []
        with open('dict/stopwords.dict', encoding='utf8') as f:
            for line in f:
                list_stopword.append(line)
        # 返回读取到的二本词典，一本列表
        return dict_keyword,dict_jieba,list_stopword

    def cut_word(self, sentence):
        result_g = {}
        sentence = sentence.lower()
        s_length = len(sentence)
        while s_length > 0:
            word = sentence
            w_length = len(word)
            while w_length > 0:
                if word in self.dict_first:
                    if word in self.list_one:
                        break
                    if len(word) != 1:
                        result_g[word] = self.dict_first.get(word)
                    sentence = sentence[w_length:]
                    break
                elif word in self.dict_second:
                    if word in self.list_one:
                        break
                    if len(word) != 1:
                        result_g[word] = self.dict_second.get(word)
                    sentence = sentence[w_length:]
                    break
                elif w_length == 1:
                    # 切分至单字且不在字典中，不取该词
                    sentence = sentence[w_length:]
                    break
                else:
                    word = word[:w_length - 1]
                w_length = w_length - 1
            s_length = len(sentence)
        return result_g

    def get_weight(self, word_type):
        type_dict = json.load(open(self.file_path, encoding='utf-8'))
        if word_type in type_dict['专有名词']:
            return 3
        elif word_type in type_dict['一般名词']:
            return 2
        elif word_type in type_dict['动词']:
            return 1
        elif word_type in type_dict['形容/副词']:
            return 0.6
        else:
            return 0.2

    def insert_keyword(self, keyword, type, importance):
        checksql = 'SELECT keyword FROM keyword WHERE keyword =?'
        keywords = self.cursor_get_keyword.execute(checksql, (keyword,))
        keywordlist = []
        for i in keywords:
            keywordlist.append(i[0])
        if keyword not in keywordlist:
            sql = 'INSERT INTO keyword (keyword, type, importance) VALUES (?,?,?)'
            self.cursor_insert_keyword.execute(sql, (keyword, type, importance))

    def insert_extend(self, qa_id, items):
        if qa_id != None:
            eid = self.cursor_get_extend.execute('SELECT ex_id FROM extend WHERE qa_id=?', (qa_id,))
            for i in eid:
                ex_idlast = i[0]
            newex_id = ex_idlast + 1
            sql = 'INSERT INTO extend (qa_id,ex_id,item,sy_id) VALUES (?,?,?,?)'
            for k in items:
                self.cursor_insert_extend.execute(sql, (qa_id, newex_id, k, '0'))

    def get_qa_id(self, qu):
        query = self.cursor_get_qaid.execute('SELECT id FROM knowledge WHERE question=?', qu)
        for i in query:
            return i[0]
        return None

    def update_history(self):
        questions = self.cursor_get_history.execute("SELECT question FROM history")
        for qu in questions:
            qa_id = self.get_qa_id(qu)
            words = self.cut_word(qu[0])
            items = []
            for w in words:
                self.insert_keyword(w, words.get(w), self.get_weight(w))
                items.append(w)
        self.insert_extend(qa_id, items)
        self.conn.commit()
        self.conn.close()

    def __init__(self):
        self.file_path = 'a.json'
        self.conn = sqlite3.connect('knowledge.db')
        self.cursor_get_history = self.conn.cursor()
        self.cursor_get_qaid = self.conn.cursor()
        self.cursor_insert_keyword = self.conn.cursor()
        self.cursor_insert_extend = self.conn.cursor()
        self.cursor_get_extend = self.conn.cursor()
        self.cursor_insert_extend = self.conn.cursor()

        self.dict_first, self.dict_second, self.list_one = self.load_dict()


if __name__ == '__main__':
    a = init_cut()
    print(a.cut_word("我和你心连心"))