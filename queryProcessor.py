import tokenizer as tk
import orjson
import os
import math

# IMPORTANT: IF YOU ARE RUNNING INTO MEMORY ISSUES WE NEED TO SWITCH BACK TO JSON INSTEAD OF ORJSON!!!!!!!
all_ranges = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
              'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
              'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
              'u', 'v', 'w', 'x', 'y', 'z']

id_path = "buckets/id_to_url.json"
doc_count = 30817


class QueryMachine:
    # O(N), N being the length of our doc_count above.
    def __init__(self):
        self.inverted_indexes = {}  # dictionary of our needed dictionaries
        self.id_to_url = open_inverted(id_path)  # Load once

    # O(A+B+C), the heaviest operation being opening our needed "buckets"
    def retrieveURLS(self, query):
        query_tokens = tk.tokenize_query(query)
        doc_ids = self.query_document_match(query_tokens)
        ranked = self.ranking(query_tokens, doc_ids)
        return self.geturls([doc_id for doc_id, _ in ranked])

    # O(A+B+C) where A, B, C are the sizes of inverted indexes opened given a query
    # Our heaviest operation by far
    def query_document_match(self, query_tokens) -> list:
        intersection_queue = []
        for token in query_tokens:
            bucket = token[0]
            if bucket not in self.inverted_indexes:
                self.inverted_indexes[bucket] = open_inverted(bucket)

            if token in self.inverted_indexes[bucket]:
                intersection_queue.append(set(self.inverted_indexes[bucket][token].keys()))
            else:
                return []  # No results found, automatically fails query match

        if not intersection_queue:
            return []
        intersection = set.intersection(*intersection_queue)  

        return list(intersection)

    # O(A+B+C) where A, B, C are the LENGTHS of the document ID lists of each input
    @staticmethod
    def intersect(term_list1: list, term_list2: list):
        # TEMP CODE UNTIL WE CAN FIX SORTED INTERSECTION
        intersection = set()

        term_list1.sort()
        term_list2.sort()

        length_i = len(term_list1)
        length_j = len(term_list2)

        i = 0
        j = 0

        while i < length_i and j < length_j:
            if term_list1[i] == term_list2[j]:
                intersection.add(term_list1[i])
                i += 1
                j += 1
            elif term_list1[i] < term_list2[j]:
                i += 1
            else:
                j += 1

            if i < length_i and j < length_j and (term_list1[i] > term_list2[-1] or term_list2[j] > term_list1[-1]):
                break

        # intersection_set = set(term_list1) & set(term_list2)
        # intersection_list = list(intersection_set)
        # intersection_list.sort()
        return list(intersection)

    # O(N), where N is the number of docids passed in to retrieve urls
    def geturls(self, id_list):
        return [self.id_to_url[doc_id][0] for doc_id in id_list if doc_id in self.id_to_url]

    # FORMULA: (1 + log(tf)) * log(N/df)
    # O(1), Retrieval of the needed data is instant as we use a dictionary system,
    # as well len() operator on dictionaries is a O(1) operation
    def calc_score(self, term, docid):
        bucket = term[0]
        term_values = self.inverted_indexes[bucket][term][docid]
        term_frq = math.log(term_values[0])
        term_oc = len(self.inverted_indexes[bucket][term])

        for i in range(1, len(term_values)):
            if term_values[i] == -1:
                term_frq *= 2
            elif term_values[i] == -2:
                term_frq *= 1.5
            elif term_values[i] == -3:
                term_frq *= 1.2

        return (1 + term_frq) * math.log(doc_count / term_oc)

    # returns top urls, ordered (by score) doc_ids to retrieve
    # O(N*M), Where N is the number of document ids passed in and M is the number of tokens.
    # the outer for loop runs N times while the inner for loop runs M times, to calc the score of each.
    def ranking(self, query_tokens, doc_ids):
        score_max = 0   # contains max score seen so far.
        token_max = [0] * len(query_tokens)  # list of tuples containing token : max score (of that term)
        # CUT DOWN FOR FASTER PROCESSING
        threshold = 100  # counts down until we've reached 50 "suitable" documents (UPDATE GIVEN TIME)
        print(f"THRESHOLD SET TO : {threshold}")
        ranked_doc_ids = []

        # Go down the list is depleted or pulled 20 worthwhile documents
        for doc in doc_ids:
            if threshold == 0:
                break

            doc_score = 0
            skip_doc = False

            for i, token in enumerate(query_tokens):
                tfidf = self.calc_score(token, doc)
                # ADDED 1.2 OF FLEX, UP IF QUERIES SUCK
                potential = 1.3 * (self.potential_max(token_max[i+1:]))

                if (doc_score + tfidf + potential) < score_max:
                    skip_doc = True
                    break
                elif tfidf > token_max[i]:
                    token_max[i] = tfidf

                doc_score += tfidf

            # Only reaches this point if it was worth storing
            if not skip_doc:
                ranked_doc_ids.append((doc, doc_score))
                threshold -= 1
            if doc_score > score_max:
                score_max = doc_score

        ranked_doc_ids.sort(key=lambda x: x[1], reverse=True)
        return ranked_doc_ids  # return top whatever results, print cuts off to top 5

    # Passes in score UP UNTIL that point
    # O(N), Where N is the number of document ids passed in (often not the full N)
    @staticmethod
    def potential_max(token_max):
        max_score = 0
        for score in token_max:
            max_score += score
        return max_score


# O(N), Where N is the size of the bucket needed to be opened/ read
def open_inverted(token):
    starting_char = token[0]
    # THIS IF BLOCK IS ONLY FOR OPENING DOC ID LIST
    if token == id_path:  # opening id_to_url
        with open(token, "rb") as file:
            return orjson.loads(file.read())

    for start in all_ranges:  # opening any of our inverted indexes
        if start == starting_char:
            filename = f"buckets/inverted_index_{start}.json"
            if os.path.exists(filename):
                with open(filename, "rb") as file:
                    return orjson.loads(file.read())
            break
    # somehow wasn't found, shouldn't happen
    return {}