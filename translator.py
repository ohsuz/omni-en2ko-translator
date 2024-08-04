import os
import sys
import argparse
from tqdm.auto import tqdm
from datasets import Dataset, load_dataset
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import deepl
from openai import OpenAI
import urllib.request

LLM_MODEL_NAME = "nayohan/llama3-instrucTrans-enko-8b"
OPENAI_MODEL_NAME = "gpt-4o"


def load_data(args):
    dataset = load_dataset(args.dataset_name)
    texts = list(dataset["train"]["text"])
    ranges = [i for i in range(args.start_idx, len(texts), args.chunk_size)]
    ranges.append(len(texts))
    return texts, ranges


def upload_to_hf_hub(dataset_name, subset_name, eng, ko):
    enko_dataset = Dataset.from_dict({'eng': eng, 'ko': ko})
    enko_dataset.push_to_hub(dataset_name, subset_name)
    

def translate_llm(args):
    texts, ranges = load_data(args)
    llm = LLM(model=LLM_MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)
    sampling_params = SamplingParams(temperature=0, use_beam_search=False, max_tokens=4096)
    chats = [[
        {"role": "system", "content": "당신은 번역기 입니다. 영어를 한국어로 번역하세요."},
        {"role": "user", "content": text}
    ] for text in texts]
    prompts = [tokenizer.apply_chat_template(
        chat,
        tokenize=False,
        add_generation_prompt=True
    ) for chat in chats]
    
    for i in range(len(ranges)-1):
        start_idx, end_idx = ranges[i], ranges[i+1]
        cur_prompts = prompts[start_idx:end_idx]
        outputs = llm.generate(cur_prompts, sampling_params)
        outputs = [output.outputs[0].text for output in outputs]
        upload_to_hf_hub(f"{args.dataset_name}-llm", f"range_{end_idx}", texts[start_idx:end_idx], outputs)
        

def translate_deepl(args):
    texts, ranges = load_data(args)

    with open("./api_keys/deepl.txt", 'r') as f :
        auth_key = f.readline().strip()
    translator = deepl.Translator(auth_key)
    
    for i in range(len(ranges)-1):
        start_idx, end_idx = ranges[i], ranges[i+1]
        cur_texts = texts[start_idx:end_idx]
        outputs = []
        for text in tqdm(cur_texts):
            result = translator.translate_text(text, target_lang="KO")
            outputs.append(result.text)
        upload_to_hf_hub(f"{args.dataset_name}-deepl", f"range_{end_idx}", cur_texts, outputs)


def translate_openai(args):
    texts, ranges = load_data(args)

    with open("./api_keys/openai.txt", 'r') as f :
        auth_key = f.readline().strip()
    client = OpenAI(api_key=auth_key)
    
    for i in range(len(ranges)-1):
        start_idx, end_idx = ranges[i], ranges[i+1]
        cur_texts = texts[start_idx:end_idx]
        outputs = []
        for text in tqdm(cur_texts):
            completion = client.chat.completions.create(
                            model=OPENAI_MODEL_NAME,
                            messages=[
                                {"role": "system", "content": "Translate English to Korean."},
                                {"role": "user", "content": text}
                            ],
                            temperature = 0.0,
                            n=1
                        )
            outputs.append(completion.choices[0].message.content.strip())
        upload_to_hf_hub(f"{args.dataset_name}-openai", f"range_{end_idx}", cur_texts, outputs)


def translate_papago(args):
    texts, ranges = load_data(args)
    
    with open("./api_keys/papago.txt", 'r') as f:
        client_id = f.readline().strip()
        client_secret = f.readline().strip()
    request = urllib.request.Request("https://naveropenapi.apigw.ntruss.com/nmt/v1/translation")
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)
    
    for i in range(len(ranges)-1):
        start_idx, end_idx = ranges[i], ranges[i+1]
        cur_texts = texts[start_idx:end_idx]
        outputs = []
        for text in tqdm(cur_texts):
            encText = urllib.parse.quote(text)
            data = "source=en&target=ko&text=" + encText
            response = urllib.request.urlopen(request, data=data.encode("utf-8"))
            rescode = response.getcode()
            if rescode == 200:
                response_body = response.read()
                outputs.append(eval(response_body.decode('utf-8'))['message']['result']['translatedText'])
            else:
                outputs.append(f"Error Code: {rescode}")
        upload_to_hf_hub(f"{args.dataset_name}-papago", f"range_{end_idx}", cur_texts, outputs)

        
def main(args):
    match args.translation_type:
        case "llm":
            translate_llm(args)
        case "deepl":
            translate_deepl(args)
        case "openai":
            translate_openai(args)
        case "papago":
            translate_papago(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_name", type=str, default="ohsuz/math-gpt-4o-200k-prompt")  
    parser.add_argument("--translation_type", type=str, default="llm")
    parser.add_argument("--start_idx", type=int, default=0)  # 중간에 번역이 끊겼을 때를 위해 추가
    parser.add_argument("--chunk_size", type=int, default=1000)  # Hf hub에 업로드할 때 chunk 단위
    args = parser.parse_args()
    
    main(args)