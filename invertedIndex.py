from pathlib import Path
import json
import tokenizer
import os
from bs4 import BeautifulSoup
from urllib.parse import urldefrag
import hasher

all_ranges = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
              'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
              'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
              'u', 'v', 'w', 'x', 'y', 'z']


def main():
    simhash = hasher.SimHash()
    indexer = Indexer(simhash)
    indexer.traverse("DEV")


class Indexer:
    def __init__(self, hasher):
        self.hasher = hasher
        self.inverted_indexes = {f"{start}": {} for start in all_ranges}
        self.id_to_url = {}  # { docID: (url, hash) }
        self.doc_id = 0

    # HIGH PRIORITY
    def traverse(self, path_name):
        self.remove_inverted_index_files()

        root_dir = Path(path_name)
        try:
            count = 0
            for sub_dir in root_dir.glob("**"):  # Grabs subdirectories (effectively subdomains) for glob
                count += 1
                print(count)
                for json_file in sub_dir.glob("*.json"):  # Grabs actual json files attached to each subdomain
                    try:
                        url, content, title, heading, bold_text = self.file_parser(json_file)
                        self.push_to_inverted_index(url, content, title, heading, bold_text)

                    except json.JSONDecodeError:
                        print(f"Invalid JSON in {json_file}")
                    except PermissionError:
                        print(f"Permission denied for {json_file}")
                    except Exception as e:
                        print(f"Unexpected error with {json_file}: {e}")

            self.save_files("buckets/id_to_url.json")
            self.merge_files()
        except Exception as e:
            print(f"Unexpected error: {e}")

    @staticmethod
    def file_parser(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            url = data["url"]
            # content = data["content"]
            soup = BeautifulSoup(data["content"], "lxml")
            # Extract different text parts (text, titles, headings, bold)
            content = soup.get_text()                                                          # ARBITRARY SCORES FOR NOW
            title = " ".join([tag.get_text() for tag in soup.find_all("title")])               # x2 score multiplier
            heading = " ".join([tag.get_text() for tag in soup.find_all(["h1", "h2", "h3"])])  # x1.5 score multiplier
            bold_text = " ".join([tag.get_text() for tag in soup.find_all(["b", "strong"])])   # x1.2 score multiplier

        return url, content, title, heading, bold_text

    # HIGH PRIORITY
    # MODIFIED
    def push_to_inverted_index(self, url, content, title, heading, bold_text):
        # raw token/ term frequency
        tokens = tokenizer.tokenize(content)
        stemmed_tokens = tokenizer.tokenize_stemmed(content)
        token_list = tokenizer.union_tokens(tokens, stemmed_tokens)

        tokens_dict = tokenizer.computeWordFrequencies(token_list)
        # Union tokens and stemmed versions of the word
        title_set = set(tokenizer.tokenize(title)) | set(tokenizer.tokenize_stemmed(title))
        heading_set = set(tokenizer.tokenize(heading)) | set(tokenizer.tokenize_stemmed(heading))
        bold_set = set(tokenizer.tokenize(bold_text)) | set(tokenizer.tokenize_stemmed(bold_text))

        current_id = self.assign_id(url, token_list)

        for token, frequency in tokens_dict.items():
            value_list = [frequency]
            if token in title_set:
                value_list.append(-1)
            if token in heading_set:
                value_list.append(-2)
            if token in bold_set:
                value_list.append(-3)

            # Determine which range the token belongs to
            bucket = token[0].lower()
            for start in all_ranges:
                if start == bucket:
                    range_key = f"{start}"
                    if token not in self.inverted_indexes[range_key]:
                        self.inverted_indexes[range_key][token] = {current_id: value_list}
                    else:
                        self.inverted_indexes[range_key][token].update({current_id: value_list})
                    break

        # self.inverted_index[token].update({current_id: frequency})

    # HIGH PRIORITY
    def assign_id(self, url: str, tokens: list):
        cur_hash = self.hasher.compute(tokens)
        url, _ = urldefrag(url)
        #  Duplicate/ Near Duplicate Detection
        for _, (old_url, old_hash) in self.id_to_url.items():
            if url == old_url:
                return -1  # signal this id is BEING PASSED, do NOT bother tokenizing
            if self.hasher.hamming_distance(old_hash, cur_hash) <= 6:
                return -1

        if self.doc_id not in self.id_to_url:
            self.id_to_url[self.doc_id] = (url, cur_hash)
            self.doc_id += 1
            return self.doc_id - 1
        else:
            self.doc_id = max(self.id_to_url.keys()) + 1
            self.assign_id(url, tokens)

    @staticmethod
    def remove_inverted_index_files():
        # Remove numeric index files
        for start in all_ranges:
            filename = f"buckets/inverted_index_{start}.json"
            if os.path.exists(filename):
                os.remove(filename)

        # Remove id_to_url.json file
        if os.path.exists("buckets/id_to_url.json"):
            os.remove("buckets/id_to_url.json")

    # low priority
    def save_files(self, id_to_url_path):
        # Save files
        for start in all_ranges:
            filename = f"buckets/inverted_index_{start}.json"
            with open(filename, "w", encoding="utf-8") as inverted_index_file:
                json.dump(self.inverted_indexes[f"{start}"], inverted_index_file, indent=4, ensure_ascii=False)

        # Save id_to_url file
        with open(id_to_url_path, "w", encoding="utf-8") as id_to_url_file:
            json.dump(self.id_to_url, id_to_url_file, indent=4, ensure_ascii=False)

    @staticmethod
    def merge_files():
        json_files = [f"buckets/inverted_index_{start}.json" for start in all_ranges]
        merged_data = {}

        for file in json_files:
            if os.path.exists(file):
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        for key, value in data.items():
                            if key in merged_data:
                                print(f"Warning: Key '{key}' from {file} already exists. Keeping original value.")
                            else:
                                merged_data[key] = value
                except json.JSONDecodeError:
                    print(f"Skipping {file} due to JSON format error.")

        with open("buckets/merged.json", "w") as f:
            json.dump(merged_data, f, indent=4)


if __name__ == "__main__":
    main()