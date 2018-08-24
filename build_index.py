from iptcinfo3 import IPTCInfo
from pprint import pprint as pp
import pickle
import os
import re
from shutil import copy2
import trie


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


def create_trie(name):
    with open("REM_Keywords.txt", "r") as f:
        keyword_master = trie.TrieNode("*")
        for item in list(f):
            key = re.sub(r'\t+', "", item).rstrip()
            trie.add(keyword_master, key)

    with open(name + '.pkl', 'wb') as f:
        pickle.dump(keyword_master, f, pickle.HIGHEST_PROTOCOL)


def update_index(filepath, filename):
    full_path = filepath + "/" + filename
    print(full_path)
    info = IPTCInfo(full_path, force=True)
    keywords = []
    master_index_trie = load_obj("master_index_trie")
    #pp(master_index_trie.children)

    for item in info["keywords"]:
        keywords.append(item.decode("utf-8"))

    for item in keywords:
        print(trie.find_prefix(master_index_trie, item))
        associated_pics = trie.find_prefix(master_index_trie, item)[3]
        if type(associated_pics) == dict and full_path not in associated_pics.keys():
            trie.add_value(master_index_trie, item, filename, full_path, keywords)
            save_obj(master_index_trie, "master_index_trie")


def get_photos(root):
    rootDir = root
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        print('Found directory: %s' % dirName)
        for fname in fileList:
            update_index(dirName, fname)


#get_photos("/Volumes/My Passport for Mac/PICTURES in LR")