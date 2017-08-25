# _*_ coding: utf-8 _*_
import sqlite3
import requests
import json
import time

sw = 'KBase/dict/stopwords_new.txt'
# sw = 'dict/stopwords_new.txt'

# keyword
def keyword_init():
    response = requests.get('http://119.23.237.255/aimanage/keyword')
    res = response.json()
    keywords_dict = {}
    keyword = []
    for line in res['keywordlist']:
        keywords_dict[line["keyword"]] = line["importance"]
        keyword.append(line["keyword"])
    print('keyword_dict,keyword导入成功...')
    return keywords_dict, keyword

# extend
def extend_init():
    knowledge_dict = {}
    answer_dict = {}
    # extend 为了得到所有的qa_id
    QA = requests.get('http://119.23.237.255/aimanage/knowledge')
    resQA = QA.json()
    QA_id = []
    for line in resQA['knowledgelist']:
        QA_id.append(line["id"])
        knowledge_dict[line["id"]] = line["question"]
        answer_dict[line["id"]] = line["answer"]
    print('QA_id,knowledge_dict,answer_dict导入成功...')
    return QA_id, knowledge_dict, answer_dict

def question_init(QA_id):
    questionSeg = {}
    for qa_id in QA_id:
        #print(qa_id)
        qs = []
        EX = requests.get('http://119.23.237.255/aimanage/extend_question/'+str(qa_id)+'')
        for line in EX.json():
            u = 1
            qs.append(line["extend_list"])
        questionSeg[qa_id] = qs
    print('questionSeg导入成功...')
    return questionSeg

# 停用词模块
def stopwords_init():
    stopwords = []
    with open(sw, 'r', encoding='utf-8') as f:
        for line in f:
            stopwords.append(line.strip())
    f.close()
    print('stopwords导入成功...')
    return stopwords



# 分词模块
    # 判断该字符是否是中文字符（不包括中文标点）
def isChineseChar(charater):
    return 0x4e00 <= ord(charater) < 0x9fa6

    # 判断是否是ASCII码
def isASCIIChar(ch):
    import string
    if ch in string.whitespace:
        return False
    if ch in string.punctuation:
        return False
    return ch in string.printable

    # 词库分词
    # 分词方式1：正向最大匹配方式FMM，RMM=False
    # 分词方式2：反向最大匹配方式RMM，RMM=True
    # 里面共能接入两个字典的接口，不过目前使用的都是keyword字典
def question_seg(sentence, dict_seg, dict_seg1, RMM=True):
    result_s = ''
    s_length = len(sentence)
    english_word = ""
    if not RMM:
        while s_length > 0:
            word = sentence
            w_length = len(word)
            while w_length > 0:
                if w_length == 1:
                    result_s += word + "/"
                    sentence = sentence[w_length:]
                    break
                # 字典1
                elif word in dict_seg:
                    result_s += word + "/"
                    sentence = sentence[w_length:]
                    break
                # 字典2
                elif word in dict_seg1:
                    result_s += word + "/"
                    sentence = sentence[w_length:]
                    break
                else:
                    while w_length > 0:
                        if isASCIIChar(word[0]):
                            english_word = english_word + str(word[0])
                            word = word[1:]
                            sentence = sentence[1:]
                            w_length = len(word)
                        else:
                            if english_word:
                                result_s += english_word + "/"
                                english_word = ""
                            break
                    if word in dict_seg:
                        result_s += word + "/"
                        sentence = sentence[w_length:]
                        break
                    word = word[:w_length - 1]
                w_length = w_length - 1
            s_length = len(sentence)

    else:
        result_s = []
        while s_length > 0:
            word = sentence
            w_length = len(word)
            while w_length > 0:
                if w_length == 1:
                    # print(word)
                    result_s = word + "/" + result_s
                    sentence = sentence[:s_length - w_length]
                    break
                elif word in dict_seg:
                    result_s = word + "/" + result_s
                    sentence = sentence[:s_length - w_length]
                    break
                else:
                    while w_length > 0:
                        if isASCIIChar(word[-1]):
                            english_word = str(word[-1]) + english_word
                            word = word[:-1]
                            sentence = sentence[:-1]
                            w_length = len(word)
                        else:
                            if english_word:
                                result_s = english_word + "/" + result_s
                                english_word = ""
                            break
                    word = word[1:]
                w_length = w_length - 1
            s_length = len(sentence)
        s_length = len(result_s)
        result_s = result_s[:s_length - 3] + "\n"
    return result_s

    result_s = ''
    sentence = sentence.lower()
    s_length = len(sentence)
    while s_length > 0:
        word = sentence
        w_length = len(word)
        while w_length > 0:
            # 关键词及全局同义词切分
            if word in dict_kw:
                result_s += word
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
    #result_s = result_s[:len(result_s)-1]
    return result_s


# 去除分隔符'/'
# 功能：根据对输入问题进行分词后，分词结果中夹带着符号'/'，所以需要去掉分隔符'/'
# 输入数据words的格式如，words = '第一/定期/电能表/进行/周期/轮换/'
# seg的输出格式如，seg = ['第一','定期','电能表','进行','周期','轮换']
def deleteSparator(words):
    seg = words.strip().split('/')
    seg = seg[:-1]
    return seg

# 对分词结果删除停用词
# 功能：去除停用词
# 输入数据words的格式，words = ['第一','定期','电能表','进行','周期','轮换']
# 输出数据segword的格式，segword = ['定期','电能表','进行','周期','轮换']
def deleteStopwords(words, stopwords):
    segword = []
    for word in words:
        if word not in stopwords:
            segword.append(word)
    return segword


# 计分模块
# get_seg：经过分词模块的结果，list格式，如['电费','缴纳']
# questionSeg：所有extend的问题集，是字典格式，如{'25':[['电费','缴纳'],[...],[...]...],'26':[[...],[...],[...]]}
# keywords：关键词字典是字典格式，如{'电费':1.2,'缴纳':0.8}
def count_seg(get_seg, questionSeg, keywords_dict, knowledge_dict):
    best_point = [0]    # 相关的分数
    best_id = []        # 相关分数的id
    best_question = []  # 相关id下的问题
    best_point_value = 0  # best_point的比较阈值
    for qa_id in questionSeg.keys():
        #seg_array = questionSeg[qa_id].keys()
        #seg_array = questionSeg[qa_id]
        for seg_array in questionSeg[qa_id]:
            max_one, match, un_match, point = 0.0, 0.0, 0.0, 0.0
            u = 0.0
            # match：单个扩展问的匹配分
            for seg in get_seg:
                if seg in seg_array and seg in keywords_dict.keys():
                    match += float(keywords_dict[seg])
            # max_one：单个扩展问的最大匹配分
            for w in seg_array:
                if w in keywords_dict.keys():
                    max_one += float(keywords_dict[w])
            # 避免出现分母为零的情况
            if max_one == 0:
                max_one += 1
            # un_match：不匹配词的个数
            un_match_words = set(seg_array).symmetric_difference(set(get_seg))  # seg_arrayget与get_seg的并集 - seg_arrayget与get_seg的交集
            for un_word in un_match_words:
                if un_word in keywords_dict.keys():
                    un_match += 1
            point = (match - un_match * 1.0) / max_one    # 计算的分数
        # 匹配
            if max_one == 0 or match == 0 or match < un_match or point < best_point[0]:
            #if point < best_point[0]:
                continue
            else:
                # 与当前最优分比较
                if point >= best_point_value:
                    if qa_id not in best_id:
                        best_point.insert(0,point)
                        best_id.insert(0,qa_id)
                        best_question.insert(0,knowledge_dict[qa_id])
                    if len(best_id) > 4:  # 保证数组长度不超过5
                        best_point.pop(-1)
                        best_id.pop(-1)
                        best_question.pop(-1)
    return best_id, best_point, best_question
        # 输出 id、分数和相应问题的数组



# 训练集学习
def train(question, answer):
    # 训练模型——关键字权重值
    ques = question
    ans = answer
    # 分词、去停用词
    words = question_seg(ques, keyword_only, keyword_only, RMM=False)     # 关键字字典分词
    word = deleteSparator(words)                        # 去分隔符
    outcome = deleteStopwords(word, stopwords)          # 去停用词
    print(outcome)

    signal = True
    cycleTime = 0
    while signal:
        # 计算
        best_id, best_point, best_question = count_seg(outcome, questionSeg, keywords_dict, knowledge_dict)
        print('best_point = ', best_point)
        print('best_id    = ', best_id)
        print(best_question)

        # 线性分类
        if best_question == []:
            print('获取信息太少，请补充')
            signal = False
        elif best_question[0] == ans:  # 满足输出（Y）
            print('最优答案是：',ans)
            print('训练结束')
            signal = False

        else: # 不满足输出（N）
            cycleTime += 1
            KWeight = []
            if ans in best_question[1:]:   # 如果标准答案在best_question,则运行
                lenOfStep = (best_point[0] - best_point[best_question.index(ans)]) * 10   # 步长增加幅度
                aimAns = questionSeg[best_id[best_question.index(ans)]]    # 标准答案 ,得到相应的关键词
                ansKeyword = questionSeg[best_id[0]]     # 计算的最优答案 ，得到相应的关键词
                #adjustWord = set(aimAns).intersection(set(ansKeyword)).difference(set(ansKeyword))    # 找出不同的关键字,先交集，后差集
                adjustWord = set(aimAns).difference(set(ansKeyword))    # 找出不同的关键字,先交集，后差集
                print('ansKeyword:',ansKeyword)
                print('aimAns:',aimAns)
                print('adjustWord:',adjustWord)
                for w in adjustWord:
                    KWeight.append(keywords_dict[w])
                #print(KWeight)
                if KWeight == []:
                    print('无法训练，原因可能是重叠关键字过少')
                    signal = False
                else:
                    weightMax = max(KWeight)
                    weightMin = min(KWeight)
                    adjustWord = list(adjustWord)

                    if weightMax == 0:
                        keywords_dict[adjustWord[KWeight.index(weightMax)]] = 0.1
                    elif best_point[best_question.index(ans)] > 1:  # 当 point>1时，权重应该减小，这时point才能接近,为了避免值过小，选择最大权重值来递减
                        keywords_dict[adjustWord[KWeight.index(weightMax)]] = ( - lenOfStep + 1) * keywords_dict[adjustWord[KWeight.index(weightMax)]]    # 增加关键字的相对应权重值
                        print('KWeight:',keywords_dict[adjustWord[KWeight.index(weightMax)]])
                    else:  # 当 point<1时，权重应该增大，这时point才能接近，为了避免值超过2，选择最小权重值来递增
                        keywords_dict[adjustWord[KWeight.index(weightMin)]] = (lenOfStep + 1) * keywords_dict[adjustWord[KWeight.index(weightMin)]]    # 增加关键字的相对应权重值
                        print('KWeight:',keywords_dict[adjustWord[KWeight.index(weightMin)]])
                    signal = True
            #elif ans not in best_question:
            elif cycleTime >= 3: # 答案不在best_question中
                print('训练次数过多，跳出循环')
                signal= False


# 验证集验证
# 输入问题
def verify(question):
    words = question_seg(question, keyword_only, keyword_only, RMM=False)     # 关键字字典分词
    print('words:'+words)
    word = deleteSparator(words)                        # 去分隔符
    outcome = deleteStopwords(word, stopwords)          # 去停用词
    print('问题分词提取结果：',outcome)
    best_id, best_point, best_question = count_seg(outcome, questionSeg, keywords_dict, knowledge_dict)
    print('best_point = ', best_point)
    print('best_id    = ', best_id)
    print(best_question)
    return best_id, best_point, best_question


keywords_dict, keyword_only = keyword_init()
QA_id, knowledge_dict, answer_dict = extend_init()
questionSeg = question_init(QA_id)
stopwords = stopwords_init()

print(keywords_dict)
print(keyword_only)
print(QA_id)
print(knowledge_dict)
print(answer_dict)
print(questionSeg)
print(stopwords)

# question = '显示文件后缀名'
# a = verify(question)


