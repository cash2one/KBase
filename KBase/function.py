# -*- coding:utf-8 -*-
# @author:Eric Luo
# @file:function.py
# @time:2017/6/15
file_keyword = "KBase/dict/keyword.dict"
file_extend = "KBase/dict/extend.dict"
file_qa = "KBase/KBase/dict/knowledge.xml"

# 预加载字典文件
def load_dataframe():
    # 读取并生成关键词和全局同义词字典
    print("Building keywords dictionary...")
    dict_keyword = {}
    with open(file_keyword, encoding='utf8') as f:
        for line in f:
            (val, imp) = line.strip().split(',')
            dict_keyword[val] = imp
    print("Dict Keyword:", len(dict_keyword))

    # 读取并生成问答扩展问字典 & 局部同义词字典
    print("Building extends & local synonym dictionary...")
    dict_extend = {}
    dict_local_synonym = {}
    local_synonym = []
    with open(file_extend, encoding='utf8') as f:
        for line in f:
            (qa_ex_id, item) = line.strip().split(',')
            if item == "Extend":
                continue
            items = item.split(';')
            items.pop(-1)
            extends = []
            synonym = []
            for keyword in items:
                extends.append(keyword.split('|'))
                synonym.append(keyword.split('|'))
                local_synonym.extend(synonym.pop(0))
            dict_extend[qa_ex_id] = extends
    dict_local_synonym = {local_synonym[i]:i for i in range(0, len(local_synonym))}
    print("Dict Extends %d & local synonym: %d" % (len(dict_extend), len(dict_local_synonym)))

    # print(dict_keyword)
    # print(dict_local_synonym)
    # print(dict_extend)
    return dict_keyword, dict_local_synonym, dict_extend


# 问句分词，最大匹配算法，缺省正相匹配
def fmm_cut(sentence, dict_kw, dict_local_sy):
    result_s = []
    sentence = sentence.lower()
    s_length = len(sentence)
    while s_length > 0:
        word = sentence
        w_length = len(word)
        while w_length > 0:
            # 关键词及全局同义词切分
            if word in dict_kw:
                result_s.append(word)
                sentence = sentence[w_length:]
                break
            # 局部同义词切分
            elif word in dict_local_sy:
                result_s.append(word)
                sentence = sentence[w_length:]
                break
            # 切分至单字
            elif w_length == 1:
                result_s.append(word)
                sentence = sentence[w_length:]
                break
            else:
                word = word[:w_length - 1]
            w_length = w_length - 1
        s_length = len(sentence)
    return result_s


# 加载问答对
def load_qa(xml_filename):
    print("Building Question, Answer, Branch Dict...")
    # Process knowledge.xml
    dict_question, dict_answer = {}, {}
    qa_id = 0
    with open(file_extend, encoding='utf8') as f:
        for line in f:
            qa_id = qa_id + 1
            if line == "question":
                dict_question[qa_id] = line
            elif line == "answer":
                dict_answer[qa_id] = line
    print("The volumn of Question, Answer, Branch Dict:", len(dict_question), len(dict_answer))
    return dict_question, dict_answer


def get_qa(items):
    question, answer = [], []
    if len(items) > 4:
        max5 = 4
    else:
        max5 = len(items)
    for j in range(max5):
        qa_id = items[j]
        if int(qa_id) in dict_question:
            # print("Find question & answer!")
            question.append(dict_question.get(int(qa_id)))
            answer.append(dict_answer.get(int(qa_id)))
    return question, answer

"""
计算问句分值
* 算法说明：逐个比较keyword[]与extend.get(i)
* 1、计算该extend的最高匹配分：将其所有item根据重要性和是否可省略评分，再相加得到最高匹配分（满分）
* 2、计算keyword[]与extend的重合关键词，将重合关键词的分数相加，得到匹配分。
* 3、计算keyword[]中与extend不重合的关键词，将不重合关键词的分数相加，乘以系数，得到不匹配分
* 4、总得分 = (匹配分-不匹配分)/最高匹配分
"""


def count_point(dict_seg):
    best_id, best_point, best_extend = [], [0.55], []

    for qa_ex_id in dict_extend.keys():
        point, max_point, match, un_match = 0.0, 0.0, 0.0, 0.0

        # 计算扩展问的最大分，可事先计算好生成字典文件
        for extend in dict_extend.get(qa_ex_id):
            max_point += float(dict_keyword.get(extend[0]))

        for seg in dict_seg.keys():
            success = False
            for extend in dict_extend.get(qa_ex_id):
                items = extend
                if seg in items:
                    match += float(dict_keyword.get(items[0]))
                    success = True
                    break
            if not success and dict_keyword.get(seg):
                un_match += float(dict_keyword.get(seg)) * 0.3

        # 计算扩展问的总分point，确定是否最佳
        if max == 0 or match == 0 or match < un_match:  # max=0代表空白扩展问；match=0代表全部不匹配；match < unmatch 代表不匹配度太高
            continue
        else:
            # 计算总分
            point = (match - un_match) / max_point
            # print("qa_ex_id, point, max, match, unmatch", qa_ex_id, point, max, match, unmatch)

            # 与当前最佳分比较
            if point >= best_point[0]:
                (qa_id, _) = qa_ex_id.split(':')  # 只保留问答对序号，丢弃扩展问序号
                # 如果问答对序号不一致才加入最佳答案
                if qa_id not in best_id:
                    best_point.insert(0, point)
                    best_id.insert(0, qa_id)
                    best_extend.insert(0, dict_extend.get(qa_ex_id))
                    # print("Best qa_ex_id, point, max, match, unmatch", qa_ex_id, point, max, match, unmatch)
    best_point.pop(-1)
    print('Best ID, point, Extend:', best_id, best_point, best_extend)
    return best_id, best_point, best_extend

dict_keyword, dict_synonym, dict_extend = load_dataframe()  # 预加载字典文件，关键词、局部同义词、扩展问
dict_question, dict_answer = load_qa(file_qa)  # 预加载问答知识库问答对文件，及扩展问
