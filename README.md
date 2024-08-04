# OMNI-EN2KO-TRANSLATOR
Integrated all English-to-Korean translators (DeepL, OpenAI, Papago, LLM (nayohan/llama3-instrucTrans-enko-8b)) | 
--- | 
<p align="center"><img width="300" alt="image" src="https://github.com/user-attachments/assets/d627bc6d-845b-4aec-b056-d7ab88d7c6ba"></p> 

---
## 환경 설정
```
conda create -n translation python=3.10
conda activate translation
pip install -r requirements.txt
huggingface-cli login
```

### API KEY 설정
> `api_keys` 폴더 안의 텍스트 파일에 DeepL, OpenAI, Papago API 키를 채워넣어야 함
> 
1. Deepl & OpenAI
    - 각각 회원가입하고 아래의 링크에서 발급!
        - https://www.deepl.com/ko/your-account/keys
        - https://platform.openai.com/api-keys
2. Papago API Key 발급
    
    > 클라이언트 아이디는 [NAVER Cloud Platform 콘솔](https://console.ncloud.com/)에서 애플리케이션을 등록해 발급받습니다.
    > 
    > 1. 콘솔의 **AI Service > Papago Translation > APIs**에서 애플리케이션을 등록합니다.
    > 2. **AI Service > Papago Translation > APIs**에서 등록한 애플리케이션을 선택해 Client ID와 Client Secret값을 확인합니다.
    > 3. **AI Service > Papago Translation > APIs**의 **수정** 화면에서 **Papago Text Translation**이 선택되어 있는지 확인합니다. 선택되어 있지 않으면 429 (Quota Exceed)가 발생하니 주의해 주십시오.
    > 
    > 출처: https://api.ncloud-docs.com/docs/ai-naver-papagonmt
    >

---

## 사용법
> 예시 결과물: https://huggingface.co/datasets/ohsuz/math-gpt-4o-200k-prompt-merged
```bash
# example.sh

dataset_name="PawanKrd/math-gpt-4o-200k"
col_name="prompt"
user_name="ohsuz"
translation_types=("openai" "deepl" "papago" "llm")
chunk_size=10
last_idx=100
translated_dataset="${user_name}/math-gpt-4o-200k-${col_name}"

python converter.py --dataset_name "$dataset_name" --col_name "$col_name" --user_name "$user_name"

for type in "${translation_types[@]}"; do
  python translator.py --dataset_name "$translated_dataset" --translation_type "$type" --chunk_size "$chunk_size"
done

python merger.py --dataset_name "$translated_dataset" --translation_types "$(IFS=,; echo "${translation_types[*]}")" --chunk_size "$chunk_size" --last_idx "$last_idx"
```

1. **converter.py**
   - 오리지널 영어 데이터셋에서(`dataset_name`) `col_name`에 속하는 텍스트만 추출
   - 사용자의 허깅페이스 계정에(`user_name`) `{dataset_name}-{col_name}`이란 데이터셋명으로 재업로드
   - (translator.py 코드를 최대한 편하게 짜기 위해 이런 선택을...)
2. **translator.py**
   - `chunk_size`: 중간에 끊길 때를 대비하여 번역이 완료된 데이터들을 chunk_size 단위마다 허깅페이스 허브에 업로드
       - if chunk_size == 100, 다음의 subset 이름으로 데이터들이 업로드됨: range_100, range_200, range_300, ... range_{len(데이터셋)}
3. **merger.py**
   - 각 번역기를 통해 번역이 완료된 데이터셋들을 하나의 데이터셋으로 병합
   - `last_idx`: len(데이터셋) (마지막 subset에서 숫자 부분)

- Default LLM이나 OpenAI 모델을 바꾸고 싶은 경우
  - https://github.com/ohsuz/omni-en2ko-translator/blob/2831783ce8b9f232892ed06ce8763dbb2bf145d2/translator.py#L12-L13
