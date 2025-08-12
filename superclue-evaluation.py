from tqdm import tqdm 
import json
import re
import sys
path = sys.argv[1]
model_name = sys.argv[2]

def judge_answer(answer, check_code):
    answer = answer.replace("\n", "\\n").replace('"', '\"')
    answer = answer.replace("\'", "\\'")

    if check_code.count("{") != check_code.count("}"):
        check_code = check_code.strip("}")

    try:
        code_str = check_code + '\n\nresponse = ' + "'" + answer + "'" + "\nresult = check_response(response)\n"

        # 执行代码字符串
        exec(code_str)
    except:
        code_str = check_code + '\n\nresponse = ' + "\"" + answer + "\"" + "\nresult = check_response(response)\n"

        # 执行代码字符串
        exec(code_str)

    # 获取结果
    res = locals().get('result')
    return res

data_new = []
code_dic = {}

with open("./superclue-all-jqzl.json", "r") as f:
    for k in f:
        k = json.loads(k)
        code_dic[k["prompt"]] = k["valid_code"]

with open(path, "r") as f:
    for k in f:
        k = json.loads(k)
        query = k.get("prompt", "")
        if query == "":
            query = k["messages"][0]["content"]
        if code_dic.get(query, "") == "":
            continue
        k["valid_code"] = code_dic[query]
        data_new.append(k)

err = []
res = []
n = 0
r = 0
list_ = []
for k in tqdm(data_new):
    try:
        answer = k[model_name].split("</think>")[-1].strip()
        s = judge_answer(answer, k["valid_code"])
        k["pingce-infos"] = s
        res.append(k)
        if s["check_code"] == True:
            list_.append(1)
            r += 1
            res.append(k)
        else:
            list_.append(0)
        n += 1
    except:
        res.append(k)
        err.append(k)
        pass
print("acc is: ", r/len(data_new), r, len(data_new))
