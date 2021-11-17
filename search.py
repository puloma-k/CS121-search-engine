import pickle
from indexer import indexer, getTokenPath
from nltk.stem.porter import *

INDEX_ROOT_PATH = "/Users/puloma/Code/CS121/Assignment #3/index/part0"

def retriever(tokens_list):
    # for each token in list, get postings list
    for token in tokens_list:
        token_file_path = getTokenPath(token)
        with open(token_file_path, 'rb') as path:
            token_postings_list = pickle.load(path)
    # merge postings lists


def main():
    url_dict = {}
    # build index
    indexer(url_dict)
    # get user input
    # parse and stem tokens and send to retriever
    tokens_list = []
    # fetch urls of docs and print results
    result_docs = retriever(tokens_list)
    for doc_id in result_docs:
        print(url_dict[doc_id] + "\n")

if __name__ == "__main__":
    main()