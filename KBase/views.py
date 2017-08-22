# -*- coding:utf-8 -*-
# @author:
# @file:views.py
# @time:2017/8/22
from __future__ import unicode_literals
from flask import render_template, request
from KBase.function import *
import json
import requests
import os
from werkzeug.utils import secure_filename
from KBase import app



@app.route('/')
def index():

    return render_template('index.html')


@app.route('/keyword/keyword_tool', methods=['GET', 'POST'])
@app.route('/keyword/keyword_tool/', methods=['GET', 'POST'])
def keyword_tool():

    return render_template('keyword/keyword_tool.html')

@app.route('/keyword/keyword_query', methods=['GET', 'POST'])
@app.route('/keyword/keyword_query/', methods=['GET', 'POST'])
def keyword_query():
    limit = int(request.args['limit'])
    offset = int(request.args['offset'])
    statu = request.args['statu']
    if statu == '':
        params = "/keyword/" + str(offset) + "/" + str(limit)
    else:
        params = "/keyword/" + statu
    try:
        hg = http_get(params)
    except Exception as e:
        return json.dumps({'data' : [], 'total' : [], 'rows' : [], 'error' : 'error'})
    # lstRes = []
    # for i in range(0, 50):
    #     oModel = {'id': '', 'keyword': '', 'importance': '', 'type': ''}
    #     oModel['id'] = str(i);
    #     oModel['keyword'] = "电费" + str(i);
    #     oModel['importance'] = "权重" + str(i);
    #     oModel['type'] = "unknown";
    #     lstRes.append(oModel);
    # total = len(lstRes)
    # re = lstRes[offset:offset + limit]
    # x = {'total': total, 'rows': re}
    #
    # return json.dumps(x)

    if statu == '':
        res = hg['keywordlist']
        total = int(hg['keywordlen'])
        xs = {'total': total, 'rows': res}
    else:
        res = [hg['fromkeyword']]
        if res == [None]:
            res = []
            total = 0
        else:
            total = len(res)
        xs = {'total': total, 'rows': res}

    return json.dumps(xs)

@app.route('/keyword/keyword_add', methods=['GET', 'POST'])
@app.route('/keyword/keyword_add/', methods=['GET', 'POST'])
def keyword_add():
    if request.method == 'POST':
        flag = False
        keyword = request.form.get('keyword')
        pos = request.form.get('pos')
        values = request.form.get('values')
        mo = [{"keyword":keyword, "type":pos, "importance":values}]
        params = "/keyword"
        try:
            re = http_post(params, mo)
        except Exception as e:
            return render_template('keyword/keyword_add.html', error='error', )

        if re['result'] == "success":
            flag = True

        return render_template('keyword/keyword_add.html', add=flag, )

    return render_template('keyword/keyword_add.html')

@app.route('/keyword/keyword_delete', methods=['GET', 'POST'])
@app.route('/keyword/keyword_delete/', methods=['GET', 'POST'])
def keyword_delete():
    id = request.form.getlist('id[]')
    keyword = request.form.getlist('keyword[]')
    flag = False
    mo = []
    # print(id,keyword)
    for i in range(len(id)):
        mo.append({"id": id[i], "keyword": keyword[i]})
    params = "/keyword"
    try:
        re = http_delete(params, mo)
    except Exception as e:
        return 'error'

    app.logger.info("Delete ID: %s", id)
    app.logger.info("Delete ID: %s", re)
    if re['result'] == "success":
        flag = True
    return str(flag)

@app.route('/keyword/keyword_modify', methods=['GET', 'POST'])
@app.route('/keyword/keyword_modify/', methods=['GET', 'POST'])
def keyword_modify():
    if request.method == 'POST':
        id = request.form.get('ID')
        keyword = request.form.get('keyword')
        type = request.form.get('type')
        importance = request.form.get('importance')
        flag = False
        mo = [{"id":id, "keyword":keyword, "importance":importance, "type":type}]
        params = "/keyword"

        try:
            re = http_patch(params, mo)
        except Exception as e:
            return render_template('keyword/keyword_modify.html', error='error', )

        if re['result'] == "success":
            flag = True

        app.logger.info("Keyword: %s", keyword)

        return render_template('keyword/keyword_modify.html', modify=flag, )

    return render_template('keyword/keyword_modify.html', )


@app.route('/knowledge/standard_tool', methods=['GET', 'POST'])
@app.route('/knowledge/standard_tool/', methods=['GET', 'POST'])
def standard_tool():

    return render_template('knowledge/standard_tool.html')

@app.route('/knowledge/standard_query', methods=['GET', 'POST'])
@app.route('/knowledge/standard_query/', methods=['GET', 'POST'])
def standard_query():
    limit = int(request.args['limit'])
    offset = int(request.args['offset'])
    statu = request.args['statu']
    if statu == '':
        params = "/knowledge/" + str(offset) + "/" + str(limit)
    else:
        params = "/knowledge/" + statu
    try:
        hg = http_get(params)
    except Exception as e:
        return json.dumps({'data' : [], 'total' : [], 'rows' : [], 'error' : 'error'})
    if statu != '':
        xs = {'data': hg['knowledgelist']}
    else:
        res = hg['knowledgelist']
        total = str(hg['knowledgelen'])
        xs = {'total': total, 'rows': res}

    return json.dumps(xs)

@app.route('/knowledge/standard_add', methods=['GET', 'POST'])
@app.route('/knowledge/standard_add/', methods=['GET', 'POST'])
def standard_add():
    if request.method == 'POST':
        if request.form.get('confrim') == 'step2':
            return standard_add_step2()
        elif request.form.get('confrim') == 'step3':
            return standard_add_step3()
        elif request.form.get('confrim') == 'end':

            # 从页面获取问题、答案、已存在关键词、新加入关键词及其属性
            checkbox = request.form.getlist('checkbox')
            key_pos = []
            value_pos = []
            valueset = []
            value_pos_get = request.form.getlist('valuesin')
            valueset_get = request.form.getlist('valueset')
            mo = []
            for i in checkbox:
                h = {}
                h["keyword"] = value_pos_get[int(i)]
                h["importance"] = valueset_get[int(i)]
                h["type"] = request.form.get(i)
                mo.append(h)
                value_pos.append(value_pos_get[int(i)])
                valueset.append(valueset_get[int(i)])
                key_pos.append(request.form.get(i))
            # 输入记录至log文件中，事后分析
            app.logger.info("Checkbox: %s", checkbox)
            app.logger.info("Value pos: %s", value_pos)
            app.logger.info("Valueset: %s", valueset)
            app.logger.info("Key pos: %s", key_pos)  # 问句分词后记录至log文件中

            params = "/keyword"
            try:
                re = http_post(params, mo)
            except Exception as e:
                return render_template('index.html', error='error', )

            return render_template('knowledge/standard_add.html', )

    return render_template('knowledge/standard_add.html', )

def standard_add_step2():

    # 从页面提取问题、答案和link，然后进行分词，将分词结果传到下一个页面
    # 保存标准问答对，返回分词页面，由用户根据系统分词来重新分词
    question = request.form.get('question')
    answer = request.form.get('answer')
    link = request.form.get('link')
    mo = [{"question": question, "answer": answer, "link": link}]
    params = "/knowledge"
    try:
        re = http_post(params, mo)
    except Exception as e:
        return render_template('knowledge/standard_add.html', )

    id = re['insert_list'][0]['id']
    # print(id)
    flag = False
    if re['result'] == "success":
        flag = True
    dict_seg = {}
    seg = "";
    # todo 分词模块以及预先加载的关键词、同义词等字典
    fmm1 = fmm_cut(question, dict_keyword, dict_synonym)  # 问句分词
    for word in fmm1:
        seg = seg + "/" + word
        if word in dict_keyword:
            dict_seg[word] = float(dict_keyword.get(word))
        else:
            dict_seg[word] = 0.0
    # 输入记录至log文件中，事后分析
    app.logger.info("Question: %s", question)
    app.logger.info("Answer: %s", answer)
    app.logger.info("Seg: %s", seg)

    return render_template('knowledge/standard_add_step2.html', seg=seg, flag=flag, id=id)

def standard_add_step3():

    # 从页面获取重新分词的结果以及问题和答案，将问题、答案、新关键词、已存在关键词、已存在关键词的权重、词性、关键词传到下一个页面

    id = request.form.get('id')
    keywords = request.form.get('keywords')
    klist = keywords.split('/')
    new_keyword = []
    only_keyword = []
    old_keyword = [] # 需要包括权重、词性、关键词

    # todo 预先加载的字典
    for word in klist:
        if word in dict_keyword:
            old_keyword.append(word)
        elif word != "" and word != " " and word not in new_keyword:
            new_keyword.append(word)
    for word in klist:
        if word != "":
            only_keyword.insert(0,word)

    mo = [{"qa_id": id, "extends": [only_keyword]}]
    params = "/extend_question"
    try:
        re = http_post(params, mo)
    except Exception as e:
        return render_template('knowledge/standard_add.html', )

    app.logger.info("Keywords: %s", keywords)

    return render_template('knowledge/standard_add_step3.html', nk=new_keyword, ok=old_keyword, )

@app.route('/knowledge/standard_delete', methods=['GET', 'POST'])
@app.route('/knowledge/standard_delete/', methods=['GET', 'POST'])
def standard_delete():
    delete = request.form.getlist('delete[]')
    res = []
    mo = []
    for i in delete:
        # print(i)
        params = "/knowledge/" + i
        try:
            re = http_delete(params, mo)
        except Exception as e:
            return '1'
        # print(re)
        if re['result'] != "success":
            res.append(i)
    return '0'

@app.route('/knowledge/standard_modify', methods=['GET', 'POST'])
@app.route('/knowledge/standard_modify/', methods=['GET', 'POST'])
def standard_modify():
    if request.method == 'POST':
        if request.form.get('confrim') == 'step2':
            return standard_modify_step2()
        elif request.form.get('confrim') == 'step3':
            return standard_modify_step3()
        elif request.form.get('confrim') == 'end':

            # 从页面获取问题、答案、已存在关键词、新加入关键词及其属性
            checkbox = request.form.getlist('checkbox')
            key_pos = []
            value_pos = []
            valueset = []
            value_pos_get = request.form.getlist('valuesin')
            valueset_get = request.form.getlist('valueset')
            mo = []
            for i in checkbox:
                h = {}
                h["keyword"] = value_pos_get[int(i)]
                h["importance"] = valueset_get[int(i)]
                h["type"] = request.form.get(i)
                mo.append(h)
                value_pos.append(value_pos_get[int(i)])
                valueset.append(valueset_get[int(i)])
                key_pos.append(request.form.get(i))
            # 输入记录至log文件中，事后分析
            app.logger.info("Checkbox: %s", checkbox)
            app.logger.info("Value pos: %s", value_pos)
            app.logger.info("Valueset: %s", valueset)
            app.logger.info("Key pos: %s", key_pos)  # 问句分词后记录至log文件中

            params = "/keyword"
            try:
                re = http_post(params, mo)
            except Exception as e:
                return render_template('index.html', error='error', )
            flag = False
            if (re['result'] == 'success'):
                flag = True
            return render_template('knowledge/standard_modify.html', modify=flag, )

    return render_template('knowledge/standard_modify.html', )

def standard_modify_step2():

    # 从页面提取问题、答案和link，然后进行分词，将分词结果传到下一个页面
    # 保存标准问答对，返回分词页面，由用户根据系统分词来重新分词
    id = request.form.get('id')
    question = request.form.get('question')
    answer = request.form.get('answer')
    link = request.form.get('link')


    # 输入记录至log文件中，事后分析
    app.logger.info("Question: %s", question)
    mo = {"question": question, "answer": answer, "link": link}
    params = "/knowledge/" + str(id)
    try:
        re = http_patch(params, mo)
    except Exception as e:
        return render_template('index.html', error='error', )
    flag = False
    if (re['result'] == 'success'):
        flag = True

    dict_seg = {}
    seg = "";

    # todo 分词模块以及预先加载的关键词、同义词等字典
    fmm1 = fmm_cut(question, dict_keyword, dict_synonym)  # 问句分词
    for word in fmm1:
        seg = seg + "/" + word
        if word in dict_keyword:
            dict_seg[word] = float(dict_keyword.get(word))
        else:
            dict_seg[word] = 0.0
    # 输入记录至log文件中，事后分析
    app.logger.info("Question: %s", question)
    app.logger.info("Answer: %s", answer)
    app.logger.info("Seg: %s", seg)

    return render_template('knowledge/standard_modify_step2.html', seg=seg, flag=flag, id=id)

def standard_modify_step3():

    # 从页面获取重新分词的结果以及问题和答案，将问题、答案、新关键词、已存在关键词、已存在关键词的权重、词性、关键词传到下一个页面

    id = request.form.get('id')
    keywords = request.form.get('keywords')
    klist = keywords.split('/')
    new_keyword = []
    only_keyword = []
    old_keyword = [] # 需要包括权重、词性、关键词

    # todo 预先加载的字典
    for word in klist:
        if word in dict_keyword:
            old_keyword.append(word)
        elif word != "" and word != " " and word not in new_keyword:
            new_keyword.append(word)
    for word in klist:
        if word != "":
            only_keyword.insert(0,word)
    # print(only_keyword)
    # print("888")

    mo = [{"qa_id": id, "extends": [only_keyword]}]
    # print(mo)
    params = "/extend_question"
    try:
        re = http_post(params, mo)
    except Exception as e:
        return render_template('index.html', )

    app.logger.info("Keywords: %s", keywords)

    return render_template('knowledge/standard_modify_step3.html', nk=new_keyword, ok=old_keyword, )


@app.route('/extend/extend_tool', methods=['GET', 'POST'])
@app.route('/extend/extend_tool/', methods=['GET', 'POST'])
def extend_tool():
    return render_template('extend/extend_tool.html')

@app.route('/extend/extend_query', methods=['GET', 'POST'])
@app.route('/extend/extend_query/', methods=['GET', 'POST'])
def extend_query():
    limit = int(request.args['limit'])
    offset = int(request.args['offset'])
    statu = request.args['statu']
    if statu == '':
        return json.dumps({'data': []})
    else:
        params = "/extend_question/" + statu
    # lstRes = []
    # for i in range(0, 50):
    #     oModel = {'id': '', 'keyword': '', 'importance': '', 'type': ''}
    #     oModel['id'] = str(i);
    #     oModel['keyword'] = "电费" + str(i);
    #     oModel['importance'] = "电费" + str(i);
    #     oModel['type'] = "unknown";
    #     lstRes.append(oModel);
    # total = len(lstRes)
    # re = lstRes[offset:offset + limit]
    # x = {'total': total, 'rows': re}
    hg = http_get(params)
    res = []
    for i in hg:
        if i['extend_list'] == []:
            break
        h = {}
        h['ex_id'] = i['ex_id']
        h['extend_list'] = i['extend_list']
        h['synonym'] = str(i['synonym'])
        res.append(h)
    if res == [None]:
        res = []
        total = 0
    else:
        total = len(res)
    xs = {'data': res}

    return json.dumps(xs)

@app.route('/extend/extend_add', methods=['GET', 'POST'])
@app.route('/extend/extend_add/', methods=['GET', 'POST'])
def extend_add():
    if request.method == 'POST':
        if request.form.get('confrim') == 'step2':
            return extend_add_step2()
        elif request.form.get('confrim') == 'step3':
            return extend_add_step3()
        elif request.form.get('confrim') == 'end':

            id = request.form.get('id')
            question = request.form.get('question')
            checkbox = request.form.getlist('checkbox')
            key_pos = []
            value_pos = []
            valueset = []
            mo = []
            value_pos_get = request.form.getlist('valuesin')
            valueset_get = request.form.getlist('valueset')
            for i in checkbox:
                h = {}
                h["keyword"] = value_pos_get[int(i)]
                h["importance"] = valueset_get[int(i)]
                h["type"] = request.form.get(i)
                mo.append(h)
                value_pos.append(value_pos_get[int(i)])
                valueset.append(valueset_get[int(i)])
                key_pos.append(request.form.get(i))
            # 输入记录至log文件中，事后分析
            app.logger.info("Checkbox: %s", checkbox)  # 问句记录至log文件中
            app.logger.info("Value pos: %s", value_pos)
            app.logger.info("Valueset: %s", valueset)
            app.logger.info("Key pos: %s", key_pos)  # 问句分词后记录至log文件中

            params = "/keyword"
            try:
                re = http_post(params, mo)
            except Exception as e:
                # print(e)
                return render_template('index.html', error='error', )

            return render_template('extend/extend_add.html', )
    # 显示StandardAdd页面，输入问题ID、问题、答案
    return render_template('extend/extend_add.html', )

def extend_add_step2():

    # 保存标准问答对，返回分词页面，由用户根据系统分词来重新分词
    id = request.form.get('ID')
    question = request.form.get('question')
    dict_seg = {}
    seg = "";

    # todo 分词模块以及预先加载的关键词、同义词等字典
    fmm1 = fmm_cut(question, dict_keyword, dict_synonym)  # 问句分词
    for word in fmm1:
        seg = seg + "/" + word
        if word in dict_keyword:
            dict_seg[word] = float(dict_keyword.get(word))
        else:
            dict_seg[word] = 0.0
    # 输入记录至log文件中，事后分析
    app.logger.info("ID: %s", id)
    app.logger.info("Question: %s", question)
    app.logger.info("Seg: %s", seg)
    app.logger.info("Fmm: %s", fmm1)

    return render_template('extend/extend_add_step2.html',
                           id=id, question=question, seg=seg, )

def extend_add_step3():

    # 显示新的关键词
    id = request.form.get('id')
    # print(id)
    question = request.form.get('question')
    # print(question)
    keywords = request.form.get('keywords')
    klist = keywords.split('/')
    new_keyword = []
    old_keyword = {}
    only_keyword = []

    # todo 预先加载的字典
    for word in klist:
        if word in dict_keyword:
            old_keyword[word] = word
        elif word != "" and word != " " and word not in new_keyword:
            new_keyword.append(word)
    for word in klist:
        if word != "":
            only_keyword.append(word)
    # 输入记录至log文件中，事后分析
    app.logger.info("Keywords: %s", keywords)
    app.logger.info("klist: %s", klist)
    app.logger.info("New keyword: %s", new_keyword)

    mo = [{"qa_id": id, "extends": [only_keyword]}]
    params = "/extend_question"
    try:
        re = http_post(params, mo)
    except Exception as e:
        return render_template('knowledge/standard_add.html', )

    return render_template('extend/extend_add_step3.html', id=id, question=question, nk=new_keyword, ok=old_keyword, )

@app.route('/extend/extend_delete', methods=['GET', 'POST'])
@app.route('/extend/extend_delete/', methods=['GET', 'POST'])
def extend_delete():
    delete = request.form.getlist('delete[]')
    id = request.form.get('id')

    app.logger.info("Delete ID: %s", delete)

    params = "/extend_question"
    h = {}
    h['qa_id'] = id
    h['ex_id'] = delete
    mo = [h]
    try:
        re = http_delete(params, mo)
    except Exception as e:
        return '1'


    if re['result'] != "success":
        return '0'
    else:
        return '1'

@app.route('/extend/extend_modify', methods=['GET', 'POST'])
@app.route('/extend/extend_modify/', methods=['GET', 'POST'])
def extend_modify():
    if request.method == 'POST':
        question = request.form.get('question')
        flag = False

        if (question.strip() == '随机'):
            flag = True
        # 输入记录至log文件中，事后分析
        app.logger.info("Keyword: %s",question)

        return render_template('extend/extend_modify.html', modify=flag, )

    return render_template('extend/extend_modify.html', )

def http_get(params):
    url = app.config.get('URLB') + params
    response = requests.get(url)
    return response.json()

def http_post(params, mo):
    url = app.config.get('URLB') + params
    response = requests.post(url, json = mo)
    return response.json()

def http_patch(params, mo):
    url = app.config.get('URLB') + params
    response = requests.patch(url, json = mo)
    return response.json()

def http_delete(params, mo):
    url = app.config.get('URLB') + params
    response = requests.delete(url, json = mo)
    return response.json()


@app.route('/upload', methods=['GET', 'POST'])
@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        key = request.form.get('key')
        filename = secure_filename(file.filename)
        # print(key)

        file.save(os.path.join('upload/'+ key + '/', filename))
        return 'True'
    return render_template('upload.html')
