import argparse
from datasets import Dataset, load_dataset


def main(args):
    dataset = load_dataset(args.dataset_name)
    texts = list(dataset["train"][args.col_name])
    new_dataset = Dataset.from_dict({"text": texts})
    args.dataset_name = args.dataset_name.split("/")[-1]
    new_dataset.push_to_hub(f"{args.user_name}/{args.dataset_name}-{args.col_name}")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_name", type=str, default="PawanKrd/math-gpt-4o-200k")
    parser.add_argument("--col_name", type=str, default="prompt")
    parser.add_argument("--user_name", type=str, default="ohsuz")
    args = parser.parse_args()
    
    main(args)