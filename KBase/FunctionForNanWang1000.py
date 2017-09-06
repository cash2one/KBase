# _*_ coding: utf-8 _*_
import sqlite3
import requests
import json
import time

# keyword_last_time = time.time()
# knowledge_last_time = time.time()
# seg_last_time = time.time()
# refresh_time = 60

sw = 'KBase/dict/stopwords_new.txt'
sy = 'KBase/dict/synonym_new.txt'
# sw = 'dict/stopwords_new.txt'
# sy = 'dict/synonym_new.txt'

# {关键词：权重}字典、关键词列表
keywords_dict = {}
keywords_type_dict = {}
keywords_id_dict = {}
keyword_only = []
# {同义词：同义词}字典、同义词列表
syn_dict = {}
synonym = []
# {ID：问题}字典、{ID：答案}字典
knowledge_dict = {}
answer_dict = {}
# ID列表
QA_id = []
# {ID：扩展问}字典
questionSeg = {}
# 停用词列表
stopwords = []

# keyword
# 初始化 关键词：权重}字典、关键词列表
def keyword_init():
    response = requests.get('http://119.23.237.255/aimanage/keyword')
    res = response.json()
    keywords_type_dict = {}
    keywords_dict = {}
    keywords_id_dict = {}
    keyword = []
    for line in res['keywordlist']:
        keywords_dict[line["keyword"]] = line["importance"]
        keywords_type_dict[line["keyword"]] = line["type"]
        keywords_id_dict[line["keyword"]] = line["id"]
        keyword.append(line["keyword"])
    print('keywords_type_dict,keywords_id_dict,keyword_dict,keyword导入成功...')
    return keywords_type_dict, keywords_id_dict, keywords_dict, keyword

# synonym
# 初始化 {同义词：同义词}字典、同义词列表
def synonym_init():
    syn_dict_old = {}
    synonym = []
    kd = []
    with open(sy, 'r', encoding='utf-8') as f:
        for line in f:
            words = line.strip().split()
            syn_dict_old[words[0]] = words[1]
            synonym.append(words[0])
            kd.append(words[1])
        f.close()
    dict_1 = {}
    for word in set(synonym):
        dict_1[word] = synonym.count(word)
    syn_dict = {}
    for word in dict_1.keys():
        W = []
        if dict_1[word] == 1:
            syn_dict[word] = syn_dict_old[word]
        else:
            for line in range(len(synonym)):
                if synonym[line] == word:
                    W.append(kd[line])
            syn_dict[word] = W

    # syn_dict = {}
    # synonym = []
    # with open(sy, 'r', encoding='utf-8') as f:
    #     for line in f:
    #         words = line.strip().split()
    #         syn_dict[words[0]] = words[1]
    #         synonym.append(words[0])
    #     f.close()
    print('syn_dict, synonym导入成功...')
    return syn_dict, synonym

# question_answer
# 初始化 ID列表、{ID：问题}字典、{ID：答案}字典
def question_init():
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

# extend
# 初始化 {ID：扩展问}字典
# def extend_init(QA_id):
def extend_init():
    questionSeg = {}
    EX = requests.get('http://119.23.237.255/aimanage/extend_question')
    for qa in EX.json():
        qs = []
        for line in qa['extend']:
            qs.append(line['extend_list'])
        questionSeg[qa['qa_id']] = qs
    # for qa_id in QA_id:
    #     #print(qa_id)
    #     qs = []
    #     EX = requests.get('http://119.23.237.255/aimanage/extend_question/'+str(qa_id)+'')
    #     for line in EX.json():
    #         u = 1
    #         qs.append(line["extend_list"])
    #     questionSeg[qa_id] = qs
    print('questionSeg导入成功...')
    return questionSeg

# stopwords
# 初始化 停用词列表
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
def deleteStopwords(words):
    segword = []
    for word in words:
        if word not in stopwords:
            segword.append(word)
    return segword


# 计分模块
# get_seg：经过分词模块的结果，list格式，如['电费','缴纳']
# questionSeg：所有extend的问题集，是字典格式，如{'25':[['电费','缴纳'],[...],[...]...],'26':[[...],[...],[...]]}
# keywords：关键词字典是字典格式，如{'电费':1.2,'缴纳':0.8}
# def count_seg(get_seg, questionSeg, keywords_dict, syn_dict, knowledge_dict):
def count_seg(get_seg):
    best_point = [0]    # 相关的分数
    best_id = []        # 相关分数的id
    best_question = []  # 相关id下的问题
    best_point_value = 0  # best_point的比较阈值
    for qa_id in questionSeg.keys():
        for seg_array in questionSeg[qa_id]:
            max_one, match, un_match, point = 0.0, 0.0, 0.0, 0.0
            u = 0.0
            # match：单个扩展问的匹配分
            seg_array_match = []   # 各个拓展问的匹配关键词
            get_seg_match = []     # 问句分词结果后的匹配关键词
            for seg in get_seg:
                if seg in seg_array and seg in keywords_dict.keys():   # 关键词没有同义词情况
                    match += float(keywords_dict[seg])
                    seg_array_match.append(seg)
                    get_seg_match.append(seg)
                if seg in syn_dict.keys():   # 关键词有同义词情况
                    if syn_dict[seg] in seg_array and syn_dict[seg] in keywords_dict.keys():  # 同义词只对应一个关键词
                        #print('match',match)
                        match += float(keywords_dict[syn_dict[seg]])
                        #print('match',match)
                        seg_array_match.append(syn_dict[seg])
                        get_seg_match.append(seg)
                    else:  #同义词一对多个关键词
                        for word in syn_dict[seg]:
                            if word in seg_array:
                                match += float(keywords_dict[word])
                                seg_array_match.append(word)
                                get_seg_match.append(seg)
            # max_one：单个扩展问的最大匹配分
            for w in seg_array:
                if w in keywords_dict.keys():
                    max_one += float(keywords_dict[w])
            # 避免出现分母为零的情况
            if max_one == 0:
                max_one += 1
            # un_match：不匹配词的个数
            s1 = set(get_seg).difference(set(get_seg_match))   # 问题分词后,不匹配的关键词
            s2 = set(seg_array).difference(set(seg_array_match))    # 扩展问中，不匹配的关键词
            un_match_words = set(s1).union(set(s2))   # 不匹配关键词汇总
            for un_word in un_match_words:
                if un_word in keywords_dict.keys():
                    un_match += 1   # 以个数来衡量un_match分数
                    #un_match += float(keywords_dict[un_word])    # 以权重值来衡量un_match分数
            point = (match - un_match * 0.3) / max_one    # 计算的分数
        # 匹配
            if max_one == 0 or match == 0 or point < best_point[0] or match < un_match :  # 不满足条件的直接删除
                continue
            else:
                # 与当前最优分比较
                if point >= best_point[0]:  # 第一次出现的qa_id
                    if qa_id not in best_id:
                        best_point.insert(0,point)
                        best_id.insert(0,qa_id)
                        best_question.insert(0,knowledge_dict[qa_id])
                    else:   # qa_id相同，但评分更高情况
                        best_point[0] = point
                    if len(best_id) > 4:  # 保证数组长度不超过5
                        best_point.pop(-1)
                        best_id.pop(-1)
                        best_question.pop(-1)
    return best_id, best_point, best_question
        # 输出 id、分数和相应问题的数组



# 训练集学习
# def train(question, answer):
#     # 训练模型——关键字权重值
#     ques = question
#     ans = answer
#     # 分词、去停用词
#     words = question_seg(ques, keyword_only, synonym, RMM=False)     # 关键字字典分词
#     word = deleteSparator(words)                        # 去分隔符
#     outcome = deleteStopwords(word)          # 去停用词
#     print(outcome)
#
#     signal = True
#     cycleTime = 0
#     while signal:
#         # 计算
#         best_id, best_point, best_question = count_seg(outcome)
#         print('best_point = ', best_point)
#         print('best_id    = ', best_id)
#         print(best_question)
#
#         # 线性分类
#         if best_question == []:
#             print('获取信息太少，请补充')
#             signal = False
#         elif best_question[0] == ans:  # 满足输出（Y）
#             print('最优答案是：',ans)
#             print('训练结束')
#             signal = False
#
#         else: # 不满足输出（N）
#             cycleTime += 1
#             KWeight = []
#             if ans in best_question[1:]:   # 如果标准答案在best_question,则运行
#                 lenOfStep = (best_point[0] - best_point[best_question.index(ans)]) * 10   # 步长增加幅度
#                 aimAns = questionSeg[best_id[best_question.index(ans)]]    # 标准答案 ,得到相应的关键词
#                 ansKeyword = questionSeg[best_id[0]]     # 计算的最优答案 ，得到相应的关键词
#                 #adjustWord = set(aimAns).intersection(set(ansKeyword)).difference(set(ansKeyword))    # 找出不同的关键字,先交集，后差集
#                 adjustWord = set(aimAns).difference(set(ansKeyword))    # 找出不同的关键字,先交集，后差集
#                 print('ansKeyword:',ansKeyword)
#                 print('aimAns:',aimAns)
#                 print('adjustWord:',adjustWord)
#                 for w in adjustWord:
#                     KWeight.append(keywords_dict[w])
#                 #print(KWeight)
#                 if KWeight == []:
#                     print('无法训练，原因可能是重叠关键字过少')
#                     signal = False
#                 else:
#                     weightMax = max(KWeight)
#                     weightMin = min(KWeight)
#                     adjustWord = list(adjustWord)
#
#                     if weightMax == 0:
#                         keywords_dict[adjustWord[KWeight.index(weightMax)]] = 0.1
#                     elif best_point[best_question.index(ans)] > 1:  # 当 point>1时，权重应该减小，这时point才能接近,为了避免值过小，选择最大权重值来递减
#                         keywords_dict[adjustWord[KWeight.index(weightMax)]] = ( - lenOfStep + 1) * keywords_dict[adjustWord[KWeight.index(weightMax)]]    # 增加关键字的相对应权重值
#                         print('KWeight:',keywords_dict[adjustWord[KWeight.index(weightMax)]])
#                     else:  # 当 point<1时，权重应该增大，这时point才能接近，为了避免值超过2，选择最小权重值来递增
#                         keywords_dict[adjustWord[KWeight.index(weightMin)]] = (lenOfStep + 1) * keywords_dict[adjustWord[KWeight.index(weightMin)]]    # 增加关键字的相对应权重值
#                         print('KWeight:',keywords_dict[adjustWord[KWeight.index(weightMin)]])
#                     signal = True
#             #elif ans not in best_question:
#             elif cycleTime >= 3: # 答案不在best_question中
#                 print('训练次数过多，跳出循环')
#                 signal= False
#     return True

def train(question, answer):
    # 训练模型——关键字权重值
    # ques = '对计量校验结果又异议怎么办'
    # ans = '对计量校验结果又异议怎么办？'

    ques = question
    ans = answer
    outcome = question
    # # 分词、去停用词
    # words = question_seg(ques, keywords_dict, syn_dict, RMM=False)  # 关键字字典分词
    # word = deleteSparator(words)  # 去分隔符
    # outcome = deleteStopwords(word)  # 去停用词
    # print(outcome)

    signal = True
    cycleTime = 0
    while signal:
        # 计算
        best_id, best_point, best_question = count_seg(outcome)
        print('best_point = ', best_point)
        print('best_id    = ', best_id)
        print(best_question)

        # 线性分类
        if best_question == []:
            print('获取信息太少，请补充')
            signal = False
        elif best_question[0] == ans:  # 满足输出（Y）
            print('最优答案是：', ans)
            print('训练结束')
            signal = False

        else:  # 不满足输出（N）
            # best_id, best_point, best_question = count_seg(outcome)
            cycleTime += 1
            KWeight = []

            if ans in best_question[1:]:
                # print('YES')
                lenOfStep = best_point[0] - best_point[best_question.index(ans)]  # 步长增加幅度
                QuesKeyword = outcome  # 问句分词
                aimAns = questionSeg[best_id[best_question.index(ans)]]  # 标准答案 ,得到相应的关键词
                ansKeyword = questionSeg[best_id[0]]  # 计算的最优答案 ，得到相应的关键词
                # adjustWord = set(aimAns).intersection(set(ansKeyword)).difference(set(ansKeyword))    # 找出不同的关键字,先交集，后差集
                adjustWord = set(aimAns).difference(set(ansKeyword))  # 找出不同的关键字,先交集，后差集
                print('ansKeyword:', ansKeyword)
                print('aimAns:', aimAns)
                print('adjustWord:', adjustWord)
                for w in adjustWord:
                    KWeight.append(keywords_dict[w])
                # print(KWeight)
                if KWeight == []:
                    print('无法训练，原因可能是重叠关键字过少')
                    signal = False
                else:
                    weightMax = max(KWeight)
                    weightMin = min(KWeight)
                    adjustWord = list(adjustWord)

                    if weightMin > 2:  # 权重值不能超过2.0
                        signal = False
                    else:
                        if weightMax == 0:
                            keywords_dict[adjustWord[KWeight.index(weightMax)]] = 0.1
                        elif best_point[best_question.index(
                                ans)] > 1:  # 当 point>1时，权重应该减小，这时point才能接近,为了避免值过小，选择最大权重值来递减
                            keywords_dict[adjustWord[KWeight.index(weightMax)]] = (- lenOfStep * 10 + 1) * \
                                                                                  keywords_dict[adjustWord[
                                                                                      KWeight.index(
                                                                                          weightMax)]]  # 增加关键字的相对应权重值
                            print('KWeight:', keywords_dict[adjustWord[KWeight.index(weightMax)]])
                        else:  # 当 point>1时，权重应该增大，这时point才能接近，为了避免值超过2，选择最小权重值来递增
                            keywords_dict[adjustWord[KWeight.index(weightMin)]] = (lenOfStep * 2 + 1) * \
                                                                                  keywords_dict[adjustWord[
                                                                                      KWeight.index(
                                                                                          weightMin)]]  # 增加关键字的相对应权重值
                            print('KWeight:', keywords_dict[adjustWord[KWeight.index(weightMin)]])
                        signal = True
            # elif ans not in best_question:
            elif cycleTime >= 5:
                print('训练次数过多，跳出循环')
                signal = False
    return True


# 验证集验证
# 输入问题
def verify(question):
    words = question_seg(question, keywords_dict, synonym, RMM=False)     # 关键字字典分词
    print('words:'+words)
    word = deleteSparator(words)                        # 去分隔符
    outcome = deleteStopwords(word)          # 去停用词
    print('问题分词提取结果：',outcome)
    best_id, best_point, best_question = count_seg(outcome)
    print('best_point = ', best_point)
    print('best_id    = ', best_id)
    print(best_question)
    return best_id, best_point, best_question


# def keyword_refresh():
#     time1 = time.time()
#     global keyword_last_time
#     now_time = time.time()
#     if (now_time - keyword_last_time > refresh_time):
#         global keywords_type_dict,keywords_dict, keywords_only
#         keywords_type_dict, keywords_dict, keyword_only = keyword_init()
#
#         keyword_last_time = time.time()
#     time2 = time.time()
#     print(time2 - time1)
#
#
# def knowledge_refresh():
#     time1 = time.time()
#     global knowledge_last_time
#     now_time = time.time()
#     if (now_time - knowledge_last_time > refresh_time):
#         global QA_id, knowledge_dict, answer_dict
#         QA_id, knowledge_dict, answer_dict = question_init()
#
#         knowledge_last_time = time.time()
#     time2 = time.time()
#     print(time2 - time1)
#
#
# def seg_refresh():
#     time1 = time.time()
#     global seg_last_time
#     now_time = time.time()
#     if (now_time - seg_last_time > refresh_time):
#         global questionSeg
#         questionSeg = extend_init()
#
#         seg_last_time = time.time()
#     time2 = time.time()
#     print(time2 - time1)

def refresh():
    global keywords_type_dict, keywords_id_dict, keywords_dict, keyword_only, QA_id, knowledge_dict, answer_dict, questionSeg
    try:
        keywords_type_dict, keywords_id_dict, keywords_dict, keyword_only = keyword_init()
        QA_id, knowledge_dict, answer_dict = question_init()
        questionSeg = extend_init()
    except Exception as e:
        return e

    return True

def dict_init():
    global keywords_type_dict, keywords_id_dict, keywords_dict, keyword_only, QA_id, knowledge_dict, answer_dict, questionSeg, stopwords, syn_dict, synonym
    try:
        keywords_type_dict, keywords_id_dict, keywords_dict, keyword_only = keyword_init()
        QA_id, knowledge_dict, answer_dict = question_init()
        questionSeg = extend_init()
        stopwords = stopwords_init()
        syn_dict, synonym = synonym_init()
    except Exception as e:
        return e

    return True

def db_refresh():
    try:
        url = 'http://119.23.237.255/aimanage/keyword'
        mo = []
        for word in keywords_dict:
            mo.append({"id": keywords_id_dict[word], "keyword": word, "importance": keywords_dict[word], "type": keywords_type_dict[word]})
        response = requests.patch(url, json=mo)
        re = response.json()
        print(re['update_nums'])
        return response.json()
    except Exception as e:
        print(e)
        return False

# test
dict_init()
print(keywords_id_dict)
print(keywords_type_dict)
print(keywords_dict)
print(keyword_only)
print(QA_id)
print(knowledge_dict)
print(answer_dict)
print(questionSeg)
print(stopwords)
print(syn_dict)
print(synonym)

# question = '显示文件后缀名'
# a = verify(question)


