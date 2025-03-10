import re
from nltk.stem import PorterStemmer

STOP_WORDS = [
    "s", "ve", "d", "ll", "t",
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "cannot", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he",
    "her", "here", "hers", "herself", "him", "himself", "his", "how", "i",
    "if", "in", "into", "is", "it", "its", "itself", "me", "more", "most",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there",
    "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "whom", "why", "with",
    "would", "you", "your", "yours", "yourself", "yourselves"]

ps = PorterStemmer()


def tokenize(content: str) -> list:
    if not content:
        return []
    else:
        pattern = r"[a-zA-Z0-9]+"
        token_list = re.findall(pattern, content.lower())
        return token_list


def tokenize_stemmed(content: str) -> list:
    if not content:
        return []
    else:
        pattern = r"[a-zA-Z0-9]+"
        tokens = re.findall(pattern, content.lower())
        stemmed_list = [ps.stem(token) for token in tokens]
        return stemmed_list


def tokenize_query(query: str) -> list:
    if not query:
        return []
    else:
        token_list = []
        pattern = r"[a-zA-Z0-9]+"
        term_list = re.findall(pattern, query.lower())
        for term in term_list:
            if term not in STOP_WORDS and term not in token_list:
                token_list.append(term)
        return token_list


def union_tokens(token_list, stemmed_list):
    all_list = []
    for token, stemmed in zip(token_list, stemmed_list):
        all_list.append(token)
        if token != stemmed:
            all_list.append(stemmed)  # only add stemmed when it's different, to avoid double counting
    return all_list


def computeWordFrequencies(token_list: list) -> dict:
    token_dict = {}

    for token in sorted(token_list):
        # if token in STOP_WORDS:
        #     continue
        if token in token_dict:
            token_dict[token] += 1
        else:
            token_dict[token] = 1
    return token_dict
    # return dict(sorted(token_dict.items(), key=lambda item: item[1], reverse=True))