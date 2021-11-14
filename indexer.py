import os
import json
import re
import pickle
import shutil
from pprint import pprint
from typing import DefaultDict
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
from collections import defaultdict
from bs4 import BeautifulSoup

INDEX_THRESHOLD = 10
INDEX_ROOT_PATH = "/Users/puloma/Code/CS121/Assignment #3/index"
DATA_ROOT_PATH = "/Users/puloma/Code/CS121/Assignment #3/DEV"

def getListOfFiles(root_dir, curr_dir):
    # create a list of file and sub directories 
    listOfFile = os.listdir(root_dir + "/" + curr_dir)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        fullPath = os.path.join(root_dir + "/" + curr_dir, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(root_dir, curr_dir + "/" + entry)
        else:
            allFiles.append(curr_dir + "/" + entry)
    return allFiles

def get_clean_text(text):
    return re.sub(r'[^\w\s]', '', BeautifulSoup(text, "lxml").text)

def computeWordFrequencies(d, tokens):
    for token in tokens:
            d[token] += 1

def getTokenPath(token):
    hex_string = hex(hash(token))[2:].zfill(16)
    hex_list = list (hex_string[0+i:2+i] for i in range(0, len(hex_string), 2))
    return "/".join(hex_list) + ".data"

def writeToFile(filepath, postings_list):
    f_dir = os.path.dirname(filepath)
    if f_dir:
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
    # print(filepath)
    with open(filepath, "wb") as file:
        # print(vars(file))
        pickle.dump(postings_list, file)

def offloadIndex(inverted_index, partition_num):
    for token in inverted_index:
        tokenPath = INDEX_ROOT_PATH + "/part" + str(partition_num) + "/" + getTokenPath(token)
        writeToFile(tokenPath, inverted_index[token])

def mergeIndex(source_num, dest_num):
    token_file_path_list = getListOfFiles(INDEX_ROOT_PATH + "/part" + str(source_num), "")
    for token_file_path in token_file_path_list:
        source_file_path = INDEX_ROOT_PATH + "/part" + str(source_num) + token_file_path
        dest_file_path = INDEX_ROOT_PATH + "/part" + str(dest_num) + token_file_path
        if os.path.isdir(dest_file_path):
            continue
        if os.path.exists(dest_file_path):
            with open(dest_file_path, 'rb') as dest:
                dest_postings_list = pickle.load(dest)
        else:
            f_dir = os.path.dirname(dest_file_path)
            if f_dir:
                if not os.path.exists(f_dir):
                    os.makedirs(f_dir)
            dest_postings_list = []
        with open(source_file_path, 'rb') as source:
            source_postings_list = pickle.load(source)

        dest_postings_list.append(source_postings_list)
        with open(dest_file_path, 'w+b') as dest:
            pickle.dump(dest_postings_list, dest)

def mergeIndexes(num_partitions):
    for part_num in range(1, num_partitions):
        mergeIndex(part_num, 0)
        shutil.rmtree(INDEX_ROOT_PATH + "/part" + str(part_num))

def main():
    path_list = getListOfFiles(DATA_ROOT_PATH, "")
    num_total_postings = 0
    num_partitions = 0

    # url_id = {}
    inverted_index = defaultdict(list)
    counter = 0
    stemmer = PorterStemmer()
    for filepath in path_list:
        freq_dict = defaultdict(int)
        filepath = DATA_ROOT_PATH + "/" + filepath
        if os.path.isfile(filepath):
            with open(filepath) as f:
                data = json.load(f)
                # url = data['url']
                # url_id[counter] = url
                text = get_clean_text(data['content'])
                tokens = word_tokenize(text)
                computeWordFrequencies(freq_dict, tokens)
                for token in set(tokens):
                    # stem each token using porter stemming method
                    token = stemmer.stem(token)
                    inverted_index[token].append([counter, freq_dict[token]])
                    num_total_postings += 1
                counter += 1
            if counter == 5:
                break
            if num_total_postings >= INDEX_THRESHOLD:
                offloadIndex(inverted_index, num_partitions)
                num_partitions += 1

    mergeIndexes(num_partitions)                

    # pprint(inverted_index)

if __name__ == "__main__":
    main()
    