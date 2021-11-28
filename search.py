import pickle
import os
from pprint import pprint
from nltk.tokenize import word_tokenize
from indexer import indexer, getTokenPath
from nltk.stem.porter import *
import traceback

INDEX_ROOT_PATH = "/Users/puloma/Code/CS121/Assignment #3/index/part0"

def retriever(tokens_list):
    # for each token in list, get postings list
    all_tokens_postings = []
    for token in tokens_list:
        token_file_path = INDEX_ROOT_PATH + "/" + getTokenPath(token)
        if not os.path.exists(token_file_path):
            return []
        with open(token_file_path, 'rb') as path:
            all_tokens_postings.append(pickle.load(path))
    
    # take all curent postings and put in list
    # check if docs of all curr postings are the same
    # if so: add doc id in results list, and increment all indexes in index list
    # else: find first min doc id and increment corresponding index in index list
    # clear curr postings   
    results_list = set()
    curr_postings = []
    index_list = [0 for token in tokens_list]
    end_not_reached = True

    # while each token's posting list has not been fully traversed
    while end_not_reached:
        # for all tokens postings lists, add curr posting pointed to by index_list[i]
        for i in range(len(all_tokens_postings)):
            curr_postings.append(all_tokens_postings[i][index_list[i]])
        # if doc IDs of all curr postings match, then increment all index pointers
        if all(x[0] == curr_postings[0][0] for x in curr_postings):
            for i in range(len(index_list)):
                index_list[i] += 1
                # ensure that new index pointer does not go out of range of token posting list
                if index_list[i] >= len(all_tokens_postings[i]):
                        end_not_reached = False
                        break
            # add doc ID to results list
            results_list.add(curr_postings[0][0])
        # if doc IDs don't match, then increment index pointer of all postings lists that
        # currently point to a posting with min doc ID
        else:
            min_doc_id = min([x[0] for x in curr_postings])
            for i, posting in enumerate(curr_postings):
                if posting[0] == min_doc_id:
                    index_list[i] += 1
                    if index_list[i] >= len(all_tokens_postings[i]):
                        end_not_reached = False
                        break
        # clear curr posting so it can be rebuilt with new index pointers postings
        curr_postings = []
    return results_list

def main():
    url_dict = {}
    stemmer = PorterStemmer()

    # build index
    indexer(url_dict)

    # get user input
    while True:
        user_input = input("Enter query: ")
        
        # parse and stem tokens and send to retriever
        tokens_list = word_tokenize(user_input)
        for index, token in enumerate(tokens_list):
            tokens_list[index] = stemmer.stem(token).lower()

        # fetch urls of docs and print results
        result_docs = retriever(tokens_list)
        if not result_docs:
            print("No results found")
        for doc_id in result_docs:
            print(url_dict[doc_id] + "\n")

if __name__ == "__main__":
    main()