# SMVQA: Street Map Visual Question Answering
SMVQA is a novel text-centric visual question answering (VQA) benchmark based on real-world street map images. It contains approximately **10,000 map images** from OpenStreetMap, each annotated with detailed geospatial information, enabling the automatic generation of up to **55,000 QA pairs** across five representative question types.

Designed to evaluate large multimodal models (LMMs), SMVQA challenges models to perform OCR-based text understanding and complex geospatial reasoning. An additional test split is provided to assess generalization to out-of-domain images and novel reasoning scenarios. Evaluations of current state-of-the-art LMMs, such as GPT-4o, show that SMVQA remains a highly challenging benchmark, leaving ample room for model improvement.


## Prerequisites

#### Environment prepration

We recommend downloading [Anaconda](https://www.anaconda.com/) first and then creating a new environment with the following command:

``` shell
$ conda create -n smvqa python==3.10
```

This command will create a new environment named `smvqa` with all the required packages. To activate the environment, run:

``` shell
$ conda activate smvqa
```

After this, install some necessary packages.

```bash
$ pip install -r requirements.txt
```


#### Setup 
Our datasets is available here: [OneDrive]() or [BaiduYun](), please download and place them as follow:


```angular2html
|-- smvqa
	|-- datasets
	|  |-- test
	|  |-- test_uk
	|  |-- train
	|  |-- val
	|-- outputs
	|-- samples
	|-- scrips
...
```


#### Running
Openai API key is necessary.

Finding the code in scrips/gpt4o_example_mutil_img_inference.py and use your own api_key here

``` python
client = OpenAI(
    base_url="****",
    api_key='sk-****'
)
```

or

```python
client = OpenAI(api_key='sk-****')
```

```bash
$ python scrips/gpt4o_example_mutil_img_inference.py
```

#### Evaluation
```bash
$ python scrips/eval_smvqa.py
```


## Citation

If this repository is helpful for your research, we'd really appreciate it if you could cite the following paper:


