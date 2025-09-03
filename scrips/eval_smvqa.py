import json
import re
import sys

# 重新配置标准输出为utf-8编码
sys.stdout.reconfigure(encoding='utf-8')


directions = [
    "north", "south", "east", "west",
    "northeast", "northwest", "southeast", "southwest"
]

###location
def extract_words(text):
    words_to_find = ['top', 'bottom', 'right', 'left', 'center']
    pattern = r'\b(' + '|'.join(words_to_find) + r')\b'
    found_words = re.findall(pattern, text, re.IGNORECASE)
    return found_words

def sort_words(words):
    # 自定义排序顺序
    order = {'top': 1, 'bottom': 2, 'left': 3, 'right': 4, 'center': 5}
    # 确保输入是列表，然后进行排序
    if isinstance(words, list):
        words.sort(key=lambda x: order.get(x.lower(), 6))  # 默认值6用于未在order字典中找到的情况
    return words

###route
def find_first_direction(text):
    # 创建正则表达式来匹配方向列表中的任何一个词
    pattern = r'\b(' + '|'.join(directions) + r')\b'
    # 搜索第一个匹配的方向词
    match = re.search(pattern, text, re.IGNORECASE)
    # 如果找到匹配项，返回匹配的方向词，否则返回None
    return match.group(0) if match else None

def find_action(text):
    phrases = [
    "Turn right",
    "Forward",
    "Turn left",
    "Arrive"
]
    # 将短语列表转换为正则表达式，使用 re.escape 来处理短语中可能含有的特殊字符
    pattern = r'\b(' + '|'.join(re.escape(phrase) for phrase in phrases) + r')\b'
    # 使用 re.findall 找到所有匹配的短语，re.IGNORECASE 使匹配不区分大小写
    found_phrases = re.findall(pattern, text, re.IGNORECASE)
    return found_phrases

def normalize_text(text):
    # 移除所有标点符号并转换为小写
    return re.sub(r'[^\w\s]', '', text).lower()

def count_route_matches(list1, list2):
    # 首先标准化列表中的所有字符串
    normalized_list1 = [normalize_text(item) for item in list1]
    normalized_list2 = [normalize_text(item) for item in list2]
    
    # 计算连续匹配的数量
    match_count = 0
    for item1, item2 in zip(normalized_list1, normalized_list2):
        if item1 == item2:
            match_count += 1
        else:
            break  # 一旦发现不匹配，立即终止循环
    
    return match_count

#####num
def find_first_number(sentence):
    # 正则表达式匹配任何数字序列，包括整数和浮点数
    match = re.search(r'\d+', sentence)
    if match:
        return match.group(0)  # 将匹配的字符串转换为整数
    else:
        return None





def evaluate_accuracy(true_answer, predicted_answer, question_type):
    if question_type == "num" or question_type == "exist":
        return 1 if true_answer == predicted_answer else 0
    elif question_type == "location":
        local = extract_words(sort_words(predicted_answer))
        connected_words = '-'.join(local)
        # print(connected_words)
        return 1 if connected_words == true_answer else 0
    elif question_type == "closest":
        # 检查推理结果是否包含正确的答案
        return 1 if true_answer.lower() in predicted_answer.lower() else 0
    elif question_type == "orient":
        if true_answer in directions:
            return 1 if true_answer == predicted_answer else 0
        else: 
            return 1 if true_answer.lower() in predicted_answer.lower() else 0
    elif question_type == "route" :
        true_direct = true_answer[0].split()[1].replace('.', '')
        direct = find_first_direction(predicted_answer)
        if not direct:
            return 0
        if true_direct in direct:
            actions = find_action(predicted_answer)
            true_actions = true_answer[1:]
            count = count_route_matches(actions, true_actions)
            return (count + 1) / len(true_answer)
    return 0  # 如果需要，可以为其他类型添加逻辑


def evaluate_accuracy_lenient(true_answer, predicted_answer, question_type):
    if question_type == "num":
        pre = find_first_number(predicted_answer)
        return 1 if true_answer == pre else 0
    elif question_type == "exist":
        pre = predicted_answer.split()[0].replace(',','')
        return 1 if true_answer == pre else 0
    elif question_type == "location":
        local = extract_words(sort_words(predicted_answer))
        connected_words = '-'.join(local)
        # print(connected_words)
        return 1 if connected_words == true_answer else 0
    elif question_type == "closest":
        # 检查推理结果是否包含正确的答案
        return 1 if true_answer.lower() in predicted_answer.lower() else 0
    elif question_type == "orient":
        if true_answer in directions:
            return 1 if true_answer == predicted_answer else 0
        else: 
            return 1 if true_answer.lower() in predicted_answer.lower() else 0
    elif question_type == "route" :
        true_direct = true_answer[0].split()[1].replace('.', '')
        direct = find_first_direction(predicted_answer)
        if not direct:
            return 0
        if true_direct in direct:
            actions = find_action(predicted_answer)
            true_actions = true_answer[1:]
            count = count_route_matches(actions, true_actions)
            return (count + 1) / len(true_answer)

    return 0  # 如果需要，可以为其他类型添加逻辑


def evaluate_accuracy_choice(true_answer, predicted_answer, question_type):
    if true_answer == predicted_answer:
        return 1
    pre = predicted_answer.split()[0].replace('.','')
    pattern = r'[A-D]\.'
    match = re.findall(pattern, predicted_answer)
    if match:
        pre = match[0].replace('.','')
    else:
        pre = ''

    return 1 if true_answer == pre else 0

def evaluate_accuracy_choice_false(true_answer, predicted_answer, question_type):
    # 直接比较完整的答案
    if predicted_answer in ['A','B','C','D']:
        print('xxxxxxxxxxxxxxxxxxxxxxxxx')
        if true_answer == predicted_answer:
            return 1
        else:
            return 0
        
    pattern = r'Answer:\s*([A-Z])'
    match = re.findall(pattern, predicted_answer)
    if match :
        pre = match[0]
        print(f"Answer:  {pre}")
        return  1 if true_answer == pre else 0

    pattern = r'Option\s+([A-D])'
    match = re.findall(pattern, predicted_answer, re.IGNORECASE)
    if match :
        pre = match[0]
        print(f"option:  {pre}")
        return  1 if true_answer == pre else 0
    
    pattern = r'is\s*\n*([A-D]):'
    match = re.findall(pattern, predicted_answer)
    if match :
        pre = match[0]
        print(f"is  {pre}:")
        return  1 if true_answer == pre else 0
    
    if predicted_answer.split('\n')[0].strip() in ['A','B','C','D']:
        # print(predicted_answer.split('<')[0])
        print('has 换行')
        if true_answer == predicted_answer.split('\n')[0].strip():
            return 1
        else:
            return 0
    
    # 使用正则表达式找出答案中的字母选项，例如'A.'
    pattern = r'[A-D]\.'
    match = re.findall(pattern, predicted_answer)
    
    # 如果没有找到匹配项或者格式不正确，返回"answer_false"
    if not match:
        return "answer_false"
    
    # 取出匹配到的选项，并移除点号
    pre = match[0].replace('.', '')
    
    # 比较处理过的predicted_answer的开始部分与true_answer是否相等
    return 1 if true_answer == pre else 0



def evaluate_answer(item):
    true_answer = item['answer'].strip()
    predicted_answer = item['inference'].strip()
    question_type = item['type']
    
    scores = {
        "accuracy": evaluate_accuracy_choice_false(true_answer, predicted_answer, question_type),
    }
    
    #print(true_answer)
    #print(predicted_answer)
    if scores['accuracy'] == 1:
        print("TRUE")
    else:
        print("FALSE")
    if scores['accuracy'] == 'answer_false':
        print("answer_false")
    print('-------------------------------------------')
    
    return scores

def load_data_and_evaluate(file_path):
    # 从JSON文件加载数据
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    total_num = len(data)
    # 遍历数据并评分
    results = []
    type_scores = {}
    type_nums = {}
    for item in data:
        print(item['id'])
        scores = evaluate_answer(item)
        type = item['type']
        results.append({"id": item['id'], "scores": scores})

        if scores['accuracy'] == "answer_false":
            if "answer_false" in type_scores:
                type_scores["answer_false"] += 1
            else:
                type_scores["answer_false"] = 1
                
            if "answer_false" in type_nums:
                type_nums["answer_false"] += 1
            else:
                type_nums["answer_false"] = 1
        else:
        
            # 累加每个类型的分数
            if type in type_scores:
                type_scores[type] += scores['accuracy']
            else:
                type_scores[type] = scores['accuracy']
            
            if type in type_nums:
                type_nums[type] += 1
            else:
                type_nums[type] = 1
    
    return results, type_scores, total_num, type_nums

# 指定JSON文件路径
file_path = './outputs/sample_result.json'
# 加载数据并评分
evaluation_results, total_scores_by_type, total_num, type_num = load_data_and_evaluate(file_path)

# # 打印结果

print(total_num)
print("Total scores by question type:")

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)   

new_type_nums = {}
for item in data:
    type = item['type']
    if type in new_type_nums:
        new_type_nums[type] += 1
    else:
        new_type_nums[type] = 1

total_score = 0
for question_type, score in total_scores_by_type.items():
    if question_type == 'answer_false':
         print(f"{question_type}: {type_num[question_type]}")
    else:
        num = new_type_nums[question_type]
        total_score += score
        print(f"{question_type}: {num}")
        print(f"{question_type}: score: {score}; num: {num}; arr  {score / num}")
        print('------------')
print(total_score)
print(total_score / total_num)