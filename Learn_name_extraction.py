# coding:utf-8
import Levenshtein
import requests
from bs4 import BeautifulSoup as bs
import re
from snownlp import SnowNLP
import json
import csv
import os
from gensim.models import word2vec
from gensim.models.word2vec import Word2Vec
import os
import logging
import sys
from imp import reload

def load_actor_role_dic():
    movie_actor = dict()
    with open("./cbo_actor_role","r") as r:
        lines = r.readlines()
        for line in lines:
            line = line.replace(',','\001')
            actor_role_dict = dict()
            movie_name = line.split('\001')[0]
            actor = line.split('\001')[1]
            role = line.split('\001')[2].strip()
            actor_role_dict.update({actor:actor})
            if role != '':
                actor_role_dict.update({role:actor})
            if movie_name in movie_actor.keys():
                movie_actor[movie_name].update(actor_role_dict)
            else:
                movie_actor.update({movie_name:actor_role_dict})
    print(movie_actor)
    return movie_actor

def get_hanlp_result():
    movie_dict = dict()
    with open("./人名序列example","r") as r:
    # 不同算法人名序列（此处有hmm，crf的专有名词序列hmmnz和crfnz以及hmm,crf的人名序列hmmnr和crfnr）以\002分隔，
    # 人名序列之间以\001分隔，电影与电影之间以\n分隔
        for line in r.readlines():
            print(line)
            m = line.strip("\n")
            movie = m.split("\t")[0]
            names = m.split("\t")[1].split("\002")
            hmmnr = names[0].split("\001")
            hmmnz = names[1].split("\001")
            crfnr = names[2].split("\001")
            crfnz = names[3].split("\001")
            list = [hmmnr, hmmnz, crfnr, crfnz]
            movie_dict.update({movie: list})
    print(movie_dict)
    return movie_dict

def Similarity(definite_dict,unsure_dict):
    actor_total_dict = dict()
    for i in definite_dict:
        for j in unsure_dict:
            if Levenshtein.distance(j[5:].decode('utf-8'), i.decode('utf-8')) <= 1:
                print(j[5:])
                print(Levenshtein.distance(j[5:], i))
                actor_total_dict.update({j[5:]: definite_dict[i]})
                # jaccard 距离，效果不是很好
                # else :
                #     if jaccard(j[5:], i) > 0.7:
                #         print j[5:]
                #         print jaccard(j[5:], i)
                #         actor_total_dict.update({j[5:]: definite_dict[i]})
    return actor_total_dict


# if __name__ == '__main__':
#     actor_role_dict = load_actor_role_dic()
#     movie_dict = get_hanlp_result()
#     print(actor_role_dict.keys())
#     print(movie_dict.keys())
#     for id in movie_dict.keys():
#         print(id)
#         if id in actor_role_dict.keys():
#             print("found.")
#             actor_total_dict = dict()
#             actor_total_dict = Similarity(actor_role_dict[id],movie_dict[id][2])
#             actor_total_dict.update(Similarity(actor_role_dict[id], movie_dict[id][3]))
#             actor_total_dict.update(actor_role_dict[id])
#             print(id + ' ' + actor_total_dict)
#         else:
#             print("continue.")