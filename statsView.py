import sys
import json
from urllib.parse import urlparse


commands = {
    "top50",
    "topSub",
    "topWeb"
}


# def extract_subdomain(url):
#     parsed_url = urlparse(url)
#     domain = parsed_url.netloc
#     if domain.startswith("www."):
#         domain = domain[4:]  # Removes 'www.'
#     return domain if domain else None


def main():
    # # Check if the correct number of arguments is provided
    # if len(sys.argv) != 2:
    #     print("Usage: python statsView.py <COMMAND>")
    #     return
    #
    # command = sys.argv[1]
    # if command in commands:
    jsonExtract()


def jsonExtract():
    try:
        # Load the JSON file
        with open("buckets/merged.json", 'r', encoding='utf-8') as file:
            tokens = json.load(file)
            # tokens = data[0]
            print(f"Token count: {len(tokens)}")
        with open("buckets/id_to_url.json", 'r', encoding='utf-8') as file:
            documents = json.load(file)
        #     documents = data[0]
            print(f"Document count: {len(documents)}")

    except FileNotFoundError:
        print(f"Error: JSON file  not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in .")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()