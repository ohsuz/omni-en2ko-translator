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