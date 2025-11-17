from PIL import Image
import os
import json
from tqdm import tqdm
from openai import OpenAI
import openai
import base64
from mimetypes import guess_type
import re
import random

client = OpenAI(
    base_url="****",
    api_key='sk-****'
)

#client = OpenAI(api_key='sk-****')


def local_image_to_data_url(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded_data}"

def gpt_single_img(query, data_url):
    text = "You are a Map Comprehension Assistant, please list your answers in serial numbers, e.g. 1. Location name: (specific pixel coordinates). Note: Pixel coordinates are integers."
    system = "You're a smart map understanding assistant." + \
             "Your task is to answer based on the map images and questions provided."

    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url,
                                        "detail": "high"},
                    },
                ],
            }
        ],
        max_tokens=500,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def gpt_mutli_img(query, data_url, data_url2):
    text = "You are a Map Comprehension Assistant, please list your answers in serial numbers, e.g. 1. Location name: (specific pixel coordinates). Note: Pixel coordinates are integers."
    system = "You're a smart map reading assistant." + \
             "You will be provided with a question and two street map images. The first image is the original image and the second image is a cropped sub-image that may contain key information to answer question." +\
             "Your task is to choose the correct answer from the given options to the question based on these two pictures.\n" +\
             "Note that the sub-image serves only as a hint and may contain irrelevant or incomplete information to answer the question."

    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url,
                                        "detail": "high"},
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url2,
                                        "detail": "high"},
                    },
                ],
            }
        ],
        max_tokens=500,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

IMAGE_DIR = "./datasets/test/images"
QA_PATH = "./datasets/test/all_json/test_qa_choice_pairs_unique_id.json"
SUB_IMG_DIR = "./datasets/test/one_sub_img_SMvqa_top3"
OUTPUT_PATH = "./outputs/gpt4o_HoLI_top3.json"


single_prompt="""You will be provided with an map image and a question. Let's think step by step to solve the question. Three examples of this task are shown below, please mimic their process and format.
```

<|user|> How do I get from Blippar to Pad Thai?
Options:
A. ['Walk northwest', 'Turn right', 'Forward', 'Forward', 'Arrive']
B. ['Walk northwest', 'Forward', 'Forward', 'Turn right', 'Arrive']
C. ['Walk north', 'Forward', 'Forward', 'Turn left', 'Arrive']
D. ['Walk northwest', 'Turn left', 'Forward', 'Forward', 'Arrive']
<image>{A map image.}</image>
<|assitant|> Reason: To determine the route from Blippar to Pad Thai, follow the directions based on the map.

1. **Walk northwest** on West 30th Street.
2. **Turn right** as you pass 8th Avenue.
3. **Forward** onto the path leading to Pad Thai.
4. **Forward** until you reach your destination.
Answer: A

<|user|> Which restaurant is the closest to Apple World Trade Center by walking distance?
Options:
A. McDonald
B. Stage Door Deli
<image>{A map image.}</image>
<|assitant|> Reason: To find the closest restaurant to Apple World Trade Center by walking distance, let's examine the original map.

1. **McDonald** is located on Church Street, further north.
2. **Stage Door Deli** is located on Duane Street, west of the intersection with Church Street.
Looking at the map, the restaurant with the closest walking distance is clearly **Stage Door Del** as it is closer to the Apple World Trade Center location and doesn't require a long detour.
Answer: B

<|user|> How many hairdresser shops are in this map image?
Options:
A. 9
B. 11
C. 8
D. 6
<image>{A map image.}</image>
<|assitant|> Reason: To determine the number of hairdresser shops on the map, look for symbols typically representing hairdresser shops, such as combs or similar icons. Based on the provided images, there are:

1. Pell Hair Salon
2. Amy's Hair Salon
3. Kelly Salon
4. New Chinatown Beauty Salon
There are also symbols for two additional hair salons whose names are not shown.

So there are 6 hairdresser shops.
Answer: D
```
"""   


mutil_prompt="""Let's think step by step to solve the question. Three examples of this task are shown below, please mimic their process and format.
```

<|user|> How do I get from Blippar to Pad Thai?
Options:
A. ['Walk northwest', 'Turn right', 'Forward', 'Forward', 'Arrive']
B. ['Walk northwest', 'Forward', 'Forward', 'Turn right', 'Arrive']
C. ['Walk north', 'Forward', 'Forward', 'Turn left', 'Arrive']
D. ['Walk northwest', 'Turn left', 'Forward', 'Forward', 'Arrive']
<image>{{A map image.}}</image><image>{{A sub map image.}}</image>
<|assitant|> Reason: To determine the route from Blippar to Pad Thai, follow the directions based on the map.

1. **Walk northwest** on West 30th Street.
2. **Turn right** as you pass 8th Avenue.
3. **Forward** onto the path leading to Pad Thai.
4. **Forward** until you reach your destination.
Answer: A

<|user|> Which restaurant is the closest to Apple World Trade Center by walking distance?
Options:
A. McDonald
B. Stage Door Deli
<image>{{A map image.}}</image><image>{{A sub map image.}}</image>
<|assitant|> Reason: To find the closest restaurant to Apple World Trade Center by walking distance, let's examine the original map.

1. **McDonald** is located on Church Street, further north.
2. **Stage Door Deli** is located on Duane Street, west of the intersection with Church Street.
Looking at the map, the restaurant with the closest walking distance is clearly **Stage Door Del** as it is closer to the Apple World Trade Center location and doesn't require a long detour.
Answer: B

<|user|> How many hairdresser shops are in this map image?
Options:
A. 9
B. 11
C. 8
D. 6
<image>{{A map image.}}</image><image>{{A sub map image.}}</image>
<|assitant|> Reason: To determine the number of hairdresser shops on the map, look for symbols typically representing hairdresser shops, such as combs or similar icons. Based on the provided images, there are:

1. Pell Hair Salon
2. Amy's Hair Salon
3. Kelly Salon
4. New Chinatown Beauty Salon
There are also symbols for two additional hair salons whose names are not shown.

So there are 6 hairdresser shops.
Answer: D
```
"""   


# load question and QA pairs

with open(QA_PATH, 'r', encoding='utf-8') as file:
    qa_pairs = json.load(file)

def load_existing_results(output_path):
    if os.path.exists(output_path):
        with open(output_path, 'r') as infile:
            return json.load(infile)
    return []

results = []
def save_results(results, output_path):
    with open(output_path, 'w') as outfile:
        json.dump(results, outfile, indent=4)
        
# load exiting results
results = load_existing_results(OUTPUT_PATH)
existing_ids = set(result['id'] for result in results)

cnt = 0
random.shuffle(qa_pairs)
for qa in tqdm(qa_pairs, desc="Processing QA Pairs"):
    if qa['id'] in existing_ids:
        print(f"Skipping QA pair {qa['id']} as it already exists in results.")
        continue

    image_path = os.path.join(IMAGE_DIR, qa['image'])
    data_url = local_image_to_data_url(image_path)
    image = Image.open(image_path).convert('RGB')
    W, H = image.size
    question = qa['question']
    
    
    chioce_prompt = "Answer with the option's letter from the given choices directly."

    
    parts = question.split('\n', 1)
    qs = parts[0]  
    opt = parts[1]  
    query = f"{qs}\nOptions:\n{opt}"

    subimg_dir = os.path.join(SUB_IMG_DIR, qa['id'])
    files = os.listdir(subimg_dir)
    sub_img_files = [file for file in files if file.lower().endswith('.png')]
    png_count = len(sub_img_files)

    sub_w = 0
    sub_h = 0
    data_url2 = ''
    final_query = ''
    for i, png_file in enumerate(sub_img_files, start=2):

        sub_img_path = os.path.join(subimg_dir, png_file)

        sub_image = Image.open(sub_img_path).convert('RGB')
        data_url2 = local_image_to_data_url(sub_img_path)
        sub_w, sub_h = sub_image.size



    if png_count == 0 or (sub_w > 0.85 * W and sub_h > 0.85 * H):
        final_query = f"{single_prompt}{query}"
        print(final_query)
        response = gpt_single_img(final_query, data_url)

    else: 
        #print(sub_img_path)
        position_txt_path = os.path.join(subimg_dir, "position.txt")
        with open(position_txt_path, 'r') as f:
            position_txt = f.read().strip()
        #print(position_txt)
        
        
        query_pre = f"You will be provided with two map images and a question. The first image is the original map image, which displays a larger area of the map. The second image is a zoomed-in sub-image extracted from the {position_txt} position of the original image, with the top-left corner as the origin."
        
        new_prompt = f"{query_pre} {mutil_prompt}"
        
        final_query = f"{new_prompt}{query}"
        
        print(final_query)
        # print(data_url)
        # print(data_url2)
        response = gpt_mutli_img(final_query, data_url, data_url2)
    print('-'*10)
    
    results.append({
            "id": qa['id'],
            "image": qa['image'],
            "question": qa['question'],
            "query": final_query,
            "answer":qa['answer'],
            "inference": response,
            "type": qa['type']
        })
    
    cnt += 1
    if cnt % 1 == 0:
        save_results(results, OUTPUT_PATH)
    

# 将推理结果保存到新的 JSON 文件
with open(OUTPUT_PATH, 'w') as outfile:
    json.dump(results, outfile, indent=4)

print("Inference completed and results saved.")
