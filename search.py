import pickle
import os
from pprint import pprint
from nltk.tokenize import word_tokenize
from indexer import indexer, getTokenPath
from nltk.stem.porter import *

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
    # TODO: merge postings lists
    results_list = []
    curr_postings = []
    index_list = [0 for token in tokens_list]

    while True:
        for i in range(len(all_tokens_postings)):
            curr_postings.append(all_tokens_postings[i])[index_list[i]]
        if all(x == curr_postings[0][0] for x in curr_postings):
            print("entered")
            for num in index_list:
                index_list[num] += 1
            results_list.append(curr_postings[0][0])
        else:
            index_list[index_list.index(min(index_list))] += 1
        curr_postings = []
        print(results_list)
            
    


    # 
    # take all curent postings and put in list
    # check if docs of all curr postings are the same
    # if so: add doc id in results list, and increment all indexes in index list
    # else: find first min doc id and increment corresponding index in index list
    # clear curr postings   







    # for postings in all_tokens_postings:
    #     try:
    #         if head_posting < 0:
    #             head_posting = postings[0][0]
    #         else:
    #             if head_posting != postings[0][0]:
                    

            
    #     except (IndexError):
    #         return results_list



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