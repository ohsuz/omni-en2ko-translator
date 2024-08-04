import argparse
from datasets import Dataset, load_dataset


def merge_subset(dataset_name, col_name, chunk_size, last_idx):
    merged_lst = []
    ranges = [f"range_{i}" for i in range(0, last_idx, chunk_size)][1:] + [f"range_{last_idx}"]
    for r in ranges:
        try:
            ds = load_dataset(dataset_name, r)
            merged_lst.extend(list(ds["train"][col_name]))
        except Exception as e:
            print('There is no data within the specified range.', e)
            break
    return merged_lst


def main(args):
    merge_dict = {}
    
    for translation_type in args.translation_types.split(","):
        dataset_name = f"{args.dataset_name}-{translation_type}"
        if not merge_dict:
            merge_dict["text"] = merge_subset(dataset_name, "eng", args.chunk_size, args.last_idx)
        merge_dict[translation_type] = merge_subset(dataset_name, "ko", args.chunk_size, args.last_idx)
    
    merged_dataset = Dataset.from_dict(merge_dict)
    merged_dataset.push_to_hub(f"{args.dataset_name}-merged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_name", type=str, default="ohsuz/math-gpt-4o-200k-prompt")
    parser.add_argument("--translation_types", type=str, default="openai,deepl,papago,llm")
    parser.add_argument("--last_idx", type=int, default=100)
    parser.add_argument("--chunk_size", type=int, default=10)
    args = parser.parse_args()
    
    main(args)