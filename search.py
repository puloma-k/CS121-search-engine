import pickle
import os
from pprint import pprint
from nltk.tokenize import word_tokenize
from indexer import indexer, getTokenPath
from nltk.stem.porter import *
import traceback

INDEX_ROOT_PATH = "//Users/sahiljagad/Desktop/INDEX/part0"

def retriever(tokens_list):
    # for each token in list, get postings list
    all_tokens_postings = []
    for token in tokens_list:
        token_file_path = INDEX_ROOT_PATH + "/" + getTokenPath(token)
        if not os.path.exists(token_file_path):
            return []
        with open(token_file_path, 'rb') as path:
            a = pickle.load(path)
            if not isinstance(a[0],list):
                a[0] =  [a[0]]
            all_tokens_postings.append(a)
            
    results_list = set()
    curr_postings = []
    index_list = [0 for _ in tokens_list]

    # for postings in all_tokens_postings:
    #     print(postings)
    #     print()
    
    while True:
        try:
            for i in range(len(all_tokens_postings)):
                # print(all_tokens_postings[i][index_list[i]])
                curr_postings.append(all_tokens_postings[i][index_list[i]])
            # print("currpostings: " + str(curr_postings))
            for p in curr_postings:
                if all(x[0][0] == curr_postings[0][0][0] for x in curr_postings):
                    # print("found a match in documents")
                    for i in range(len(index_list)):
                        index_list[i] += 1
                    results_list.add(curr_postings[0][0][0])
                    break
                else:
                    min_doc = min(curr_postings)
                    index_list[curr_postings.index(min_doc)] += 1
                    break
            curr_postings = []
        except Exception as e:
            exc_obj = e
            tb = ''.join(traceback.format_exception(None, exc_obj, exc_obj.__traceback__))
            # print(tb)
            # print("results list " + str(results_list))
            return results_list


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



    #return results_list

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
        # print("DONE", result_docs)
        if not result_docs:
            print("No results found")
        for doc_id in result_docs:
            print(url_dict[doc_id] + "\n")

if __name__ == "__main__":
    main()