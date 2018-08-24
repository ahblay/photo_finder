from iptcinfo3 import IPTCInfo
from pprint import pprint as pp
import pickle
import os
import re
from shutil import copy2
import trie


# Old approach using a normal dict. KEEP for now. May be faster.
def rewrite_obj_to_blank(name):
    with open("REM_Keywords.txt", "r") as f:
        keyword_master = {}
        for item in list(f):
            key = re.sub(r'\t+', "", item).rstrip()
            keyword_master[key] = []

    with open(name + '.pkl', 'wb') as f:
        pickle.dump(keyword_master, f, pickle.HIGHEST_PROTOCOL)


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

# Old approach using a normal dict. KEEP for now. May be faster.
'''
def update_index(filepath, filename):
    info = IPTCInfo(filepath + "/" + filename, force=True)
    keywords = []
    master_index = load_obj("master_index")

    for item in info["keywords"]:
        keywords.append(item.decode("utf-8"))

    for item in keywords:
        if type(master_index[item]) == list and filename not in master_index[item]:
            master_index[item].append(filename)
            save_obj(master_index, "master_index")
'''


# This approach appears to run slower. CAREFUL
def update_index(filepath, filename):
    info = IPTCInfo(filepath + "/" + filename, force=True)
    keywords = []
    master_index_trie = load_obj("master_index_trie")
    pp(master_index_trie)

    for item in info["keywords"]:
        keywords.append(item.decode("utf-8"))

    for item in keywords:
        associated_pics = trie.find_prefix(master_index_trie, item)[2]
        if type(associated_pics) == list and filename not in associated_pics:
            trie.add_value(master_index_trie, item, filename)
            save_obj(master_index_trie, "master_index_trie")


def build_index(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg"):
            update_index(directory, filename)
        else:
            continue

# Old approach using a normal dict. KEEP for now. May be faster.
'''
def get_photos(args):
    master_index = load_obj("master_index")
    photos = []
    print(args)
    for arg in args:
        if arg in master_index:
            photos.extend(master_index[arg])
    return list(set(photos))
'''


# This approach appears to run slower. CAREFUL
def get_photos(args):
    master_index_trie = load_obj("master_index_trie")
    photos = {}
    print(args)
    for arg in args:
        if trie.find_prefix(master_index_trie, arg)[0]:
            photo_keywords = trie.find_prefix(master_index_trie, arg)[3]
            photos = {**photos, **photo_keywords}
    return photos


def save_to_results(filepath):
    copy2(filepath, "results")


def clear_results():
    file_list = os.listdir("results")
    for file_name in file_list:
        os.remove("results/" + file_name)


def save_all_to_results(location, results):
    clear_results()
    for photo in results:
        save_to_results(location + "/" + photo)


# This approach appears to run slower. CAREFUL
def create_trie(name):
    with open("REM_Keywords.txt", "r") as f:
        keyword_master = trie.TrieNode("*")
        for item in list(f):
            key = re.sub(r'\t+', "", item).rstrip()
            trie.add(keyword_master, key)

    with open(name + '.pkl', 'wb') as f:
        pickle.dump(keyword_master, f, pickle.HIGHEST_PROTOCOL)

#location = "/users/abel/dropbox/test_pics"

#rewrite_obj_to_blank("master_index")
#build_index(location)

#create_trie("master_index_trie")
#master_index_trie = load_obj("master_index_trie")
#trie.add_value(master_index_trie, "Louise", "whatever")
#print(trie.find_prefix(master_index_trie, 'L'))




