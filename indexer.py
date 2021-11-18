import os
import sys
import json
import re
import pickle
import shutil
from collections import deque
from pprint import pprint
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
from collections import defaultdict
from bs4 import BeautifulSoup

# forcing Python seed to be non randomized
HASH_SEED = os.getenv("PYTHONHASHSEED")
if not HASH_SEED:
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)


INDEX_THRESHOLD = 10
INDEX_ROOT_PATH = "/Users/puloma/Code/CS121/Assignment #3/index"
DATA_ROOT_PATH = "/Users/puloma/Code/CS121/Assignment #3/DEV"

# return list of relative paths to all files within given directory
def getListOfFiles(root_dir, curr_dir):
    listOfFile = os.listdir(root_dir + "/" + curr_dir)
    allFiles = list()
    # iterate over all the entries
    for entry in listOfFile:
        fullPath = os.path.join(root_dir + "/" + curr_dir, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(root_dir, curr_dir + "/" + entry)
        else:
            allFiles.append(curr_dir + "/" + entry)
    return allFiles

def getCleanText(text):
    return re.sub(r'[^\w\s]', '', BeautifulSoup(text, "lxml").text)

# get path of directories and filename for token using hash value
def getTokenPath(token):
    # get hash value of token
    # convert to hex string and truncate the first 2 characters (which are 0x)
    # pad with 0s to make 16 character string
    hex_string = hex(hash(token))[2:].zfill(16)
    # creates list using pairs of characters from hex string
    hex_list = list (hex_string[0+i:2+i] for i in range(0, len(hex_string), 2))
    # join list values with / to create relative filepath and filename
    return "/".join(hex_list) + ".data"

def writeToFile(filepath, postings_list):
    # create full filepath and directories for token 
    f_dir = os.path.dirname(filepath)
    if f_dir:
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
    # write to file in binary to optimize disk usage
    with open(filepath, "wb") as file:
        # serialize postings list using pickle for given token and write to file
        pickle.dump(postings_list, file)

# take current contents of inverted index in memory and write to disk
def offloadIndex(inverted_index, partition_num):
    for token in inverted_index:
        tokenPath = INDEX_ROOT_PATH + "/part" + str(partition_num) + "/" + getTokenPath(token)
        writeToFile(tokenPath, inverted_index[token])

# takes postings lists from source partition and merges with data in destination partition
# using corresponding filepaths for each token
# this function will really only be called with partition 0 as the destination
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

# merge all index partitions and delete source partition once it's empty
def mergeIndexes(num_partitions):
    for part_num in range(1, num_partitions + 1):
        print("merging index number " + str(part_num))
        mergeIndex(part_num, 0)
        shutil.rmtree(INDEX_ROOT_PATH + "/part" + str(part_num))

def indexer(url_dict):
    path_list = getListOfFiles(DATA_ROOT_PATH, "")
    num_total_postings = 0
    num_partitions = 0
    inverted_index = defaultdict(list)
    doc_id = 0
    stemmer = PorterStemmer()

    for source_file_path in path_list:
        freq_dict = defaultdict(int)
        source_file_path = DATA_ROOT_PATH + "/" + source_file_path
        if os.path.isfile(source_file_path):
            with open(source_file_path) as f:
                data = json.load(f)
                url_dict[doc_id] = data['url']
                text = getCleanText(data['content'])
                for token in word_tokenize(text):
                    # stem each token using porter stemming method
                    token = stemmer.stem(token).lower()
                    freq_dict[token] += 1
                for key, value in freq_dict.items():
                    inverted_index[key].append([doc_id, value])
                    # print("shoudl be deque: " + str(type(inverted_index[key])))
                    # print("shoudl be list: " + str(type(inverted_index[key][0])))
                    num_total_postings += 1
                doc_id += 1
            if doc_id == 5:
                break
            # if index contains certain number of postings, write it to disk
            # create new index partition for each offload operation
            if num_total_postings >= INDEX_THRESHOLD:
                offloadIndex(inverted_index, num_partitions)
                inverted_index = defaultdict(list)
                num_partitions += 1

    offloadIndex(inverted_index, num_partitions)
    mergeIndexes(num_partitions)                
    # pprint(inverted_index)
    
    