import websockets
import asyncio
import language_tool_python

from ctypes import byref
from typing import Dict
from dateutil.parser import parse

import re
import json
import string
import os
import math
import socket
import pickle
import tokenizer
import tf_idf
# punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
dir = 'CACM_Clean/'


def read_document(filename):
    with open(filename, 'r') as f:
        doc = f.read()
        t = doc.split('.T', 1)
        a = t[t.__len__() - 1].split('.A', 1)
        title_exist = doc.find('.T')
        auther_exist = doc.find('.A') > title_exist
        document_exist = doc.find('.W') > doc.find('.A')
        title = ""
        auther = ""
        document = ""
        if title_exist:
            title = a[0]
        if auther_exist:
            if title_exist:
                auther = a[1].split('.W')[0]
            else:
                auther = a[0].split('.W')[0]
        if document_exist:
            if auther_exist:
                document = a[1].split('.W')[1].split('.X')[0]
            else:
                document = a[0].split('.W')[1].split('.X')[0]
        return title, document, auther


def generate_TF():
    files = os.listdir(dir)
    matrix = {}
    counter = 0
    for file in files:
        print(file)
        [title, document, auther] = read_document(dir + file)
        [title_tokens, d1] = tokenizer.tokenize(title)
        [auther_tokens, d2] = tokenizer.tokenize(auther)
        [document_token, dates] = tokenizer.tokenize(document)
        matrix[file.split('.')[0]] = (tf_idf.tf_generator(
            title_tokens + auther_tokens + document_token + dates))
        print("done")
    with open('CACM_TF.json', 'x') as w:
        w.write(json.dumps(matrix))
        w.close()


def generate_TF_Clean_And_IDF():
    with open('CACM_TF.json', 'r') as f:
        test = f.read()
        _object = json.loads(test)
        document_count = len(_object.keys())
        # print(document_count)
        # print(_object.keys())
        token_set = {}
        matrix = {}
        for key, value in _object.items():
            for key2, value2 in value.items():
                if not key2 in token_set:
                    token_set[key2] = 1
                else:
                    token_set[key2] += 1
        for key, value in _object.items():
            for token, value2 in token_set.items():
                if not token in value:
                    value[token] = 0
        # with open('CISI_TF_Clean.json', 'x') as w:
        #     w.write(json.dumps(_object))
        #     w.close()
        with open('CACM_IDF.json', 'x') as w:
            for key, value in token_set.items():
                token_set[key] = math.log10(document_count / value)
            w.write(json.dumps(token_set))
            w.close()


def generate_TF_IDF():
    tf_idf = {}
    reg = r"ca[0-9]+"
    with open('CISI_TF_Clean.json', 'r') as f:
        tf_idf = json.loads(f.read())
    with open('CISI_IDF.json', 'r') as ff:
        idf = json.loads(ff.read())
    tt = {}
    print("generate TF_IDF")
    for key, value in tf_idf.items():
        for k, v in idf.items():
            if (not re.search(reg, k)) and k.__len__() > 3:
                if not key in tt:
                    tt[key] = {}
                tt[key][k] = round(tf_idf[key][k] * v * 100, 5)
    with open('CISI_TF_IDF.json', 'x') as w:
        w.write(json.dumps(tt))
        # pickle.dump(tf_idf,f, protocol=pickle.HIGHEST_PROTOCOL)
        w.close()
    print("--------------------------------")


def read_TF_IDF(filename):
    with open(filename, 'r') as f:
        tf_idf = json.loads(f.read())
        test = {}
        for key, value in tf_idf.items():
            for k, v in value.items():
                if not k in test:
                    test[k] = []
                tt = {}
                tt['doc'] = key
                tt['value'] = v
                test[k].append(tt)
        return test
# generate_TF_IDF()


def is_bad_rule(rule):
    return rule.message == 'Possible spelling mistake found.' and len(
        rule.replacements) and rule.replacements[0][0].isupper()


def query(query, _tf_idf, k):
    matches = tool.check(query)
    matches = [rule for rule in matches if not is_bad_rule(rule)]
    query = language_tool_python.utils.correct(query, matches)
    [token, dates] = tokenizer.tokenize(query)
    idf = tf_idf.tf_generator(token)
    res_set = []
    for i in idf:
        if not i in _tf_idf:
            continue
        array = _tf_idf[i]
        s_arr = sorted(array, key=lambda x: x['value'] * 1000, reverse=True)
        if(s_arr[0]['value'] > 0):
            res_set.append([w for w in s_arr if w['value'] > 0])
    result = {}
    rr = []
    for res in res_set:
        for doc in res:
            doc_name = doc['doc']
            found = False
            for dd in rr:
                if dd['doc_name'] == doc_name:
                    found = True
                    dd['value'] += doc['value']
                    dd['repeat'] += 1
                    break
            if not found:
                rr.append(
                    {'doc_name': doc_name, 'value': doc['value'], 'repeat': 1})
            # if not doc_name in result:
            #     result[doc_name] = doc['value']
            # else:
            #     result[doc_name] += doc['value']
    return (sorted(rr, key=lambda x: x['value'] * x['repeat'], reverse=True))[0:k], query


async def hello(websocket):
    name = await websocket.recv()
    req = json.loads(f"{name}")
    print("================================================")
    print(req)
    res = {}
    if(req['action'] == 'search'):
        res = query(req['query'], cisi_tf_idf if req['dataset']
                    == 'CISI' else cacm_tf_idf, int(req['count']))
    if req['action'] == 'getDetails':
        with open(('CISI_Clean/' if req['dataset'] == 'CISI' else 'CACM_Clean/') + req['fileName'] + ".txt", 'r') as f:
            res["content"] = f.read()
    await websocket.send(json.dumps(res))
    # print(f">>> {greeting}")


async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()  # run forever
cisi_tf_idf = {}
cacm_tf_idf = {}
print("reading language tool...")
tool = language_tool_python.LanguageTool('en-US')
print("done reading language tool...")
if __name__ == "__main__":
    print("reading indices please wait...")
    print("reading CISI index")
    cisi_tf_idf = read_TF_IDF('CISI_TF_IDF.json')
    print("done reading CISI index")

    print("reading CACM index")
    cacm_tf_idf = read_TF_IDF('CACM_TF_IDF.json')
    print("done reading CACM index")

    print("done fetching the index")
    asyncio.run(main())


def evaluate(filename):
    line = ""
    res = {}
    with open(filename) as f:
        line = f.readline()
        while line:
            arr = line.split()
            if not str(int(arr[0])) in res:
                res[str(int(arr[0]))] = []
            res[str(int(arr[0]))].append(arr[1])
            line = f.readline()
        return res


def evaluate_at(diric, k):
    ev_res = {}
    files = os.listdir(diric)
    ev_obj = evaluate("data_sets/CISI/CISI.REL" if diric ==
                      "CISI_Clean_Query/" else "data_sets/CACM/qrels.text")
    pre = 0.0
    rec = 0.0
    c = 0
    for file in files:
        with open(diric + file) as f:
            counter = file[4:-4]
            print("Running test on " + file)
            q_text = f.read()
            result_set = query(q_text, cisi_tf_idf, k)[0]
            print("Done Extracting results")
            ok = 0
            for r in result_set:
                if str(counter) in ev_obj:
                    if r['doc_name'][4:] in ev_obj[str(counter)]:
                        ok += 1
            if str(counter) in ev_obj:
                ev_res['k'] = k
                ev_res[str(counter)] = {}
                ev_res[str(counter)]['precision'] = (ok/k)
                ev_res[str(counter)]['recall'] = (
                    ok/ev_obj[str(counter)].__len__())
                pre += (ok/k)
                rec += (ok/ev_obj[str(counter)].__len__())
                c += 1
                print("Precision@"+str(k)+" = " + str(ok/k))
                print("Recall = " + str(ok/ev_obj[str(counter)].__len__()))
            print("-------------------------")
    ev_res['MAP'] = pre/c
    ev_res['MRR'] = rec/c
    ev_res['number_of_q'] = c
    with open('ev_cisi_a.json', 'w') as f:
        f.write(json.dumps(ev_res))
        f.close()
    print("MAP@"+str(k)+" = " + str(pre/c))
    print("-------------------------")
    print("MRR@"+str(k)+" =" + str(rec/c))

# print("reading indices please wait...")
# print("reading CACM index")
# cisi_tf_idf = read_TF_IDF('CISI_TF_IDF.json')
# print("done reading CACM index")
# evaluate_at("CISI_Clean_Query/", 10)
