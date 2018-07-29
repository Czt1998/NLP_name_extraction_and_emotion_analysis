# coding utf-8
from snownlp import SnowNLP
import pymysql
import sys
import json
import os
from snownlp import sentiment
import re
from imp import reload
reload(sys)
pymysql.install_as_MySQLdb()

def get_data_from_iiip_db():
    # sample: (618119, 'lintao', 'P', datetime.date(2016, .0'), '我竟然在女工和小伙子那段有点泪..没流出来囧....刘若英的强调怎么那么台湾啊!小谢跟十月一样,萌~不过不喜欢大s和他这对..张曼玉和吕燕好美啊= =刘家辉那段我挺喜欢的,杨颖一点都不Angelababy。', 0)
    conn = pymysql.connect(host='192.168.235.55', user='root', passwd='iiip', db='Seeing_future', charset="utf8")
    cur = conn.cursor()
    cur.execute("select * from douban_comment")
    items = cur.fetchall()
    return items

def comment_emotion_recogize(str):
    # print str
    try:
        s = SnowNLP(str)
    except:
        print (str)
        return 0
    return s.sentiments-0.5

def get_movie_name(movie_id):
    if not os.path.exists("./movie_actor_nick_2018_example/"+movie_id+".json"):
        return None,None
    with open("./movie_actor_nick_2018_example/"+movie_id+".json",'r') as f:
        # 这个以电影id为名称的json文件中存储着有关该部电影的演员与人名的对应关系，如唐人街探案 {“刘昊然”：“然然”，“刘昊然”：“老秦”}
        actor_total_dict =json.load(f)
    actor_score = {}
    for i in actor_total_dict:
        if not actor_total_dict[i] in actor_score.keys():
            actor_score.update({actor_total_dict[i]:0})
    return actor_total_dict,actor_score

if __name__ == '__main__':
    items = get_data_from_iiip_db()
    movie_actor_dict = {}
    movie_score_dict = {}
    for i in items:
        # print (i[5])
        # print("---------")
        movie_id = str(i[0])
        short_sentence = re.split(r'，|。|；|？|…|！',str(i[5]).strip())
        # print(short_sentence)
        #将长句切割为短句

        tmp = {}
        if not movie_id in movie_actor_dict.keys():
            actor_total_dict,actor_score = get_movie_name(movie_id)
            movie_actor_dict.update({movie_id:actor_total_dict})
            movie_score_dict.update({movie_id:actor_score})
        else :
            actor_total_dict = movie_actor_dict[movie_id]
            actor_score = movie_score_dict[movie_id]
        if actor_total_dict == None:
            continue
        total_score = comment_emotion_recogize(str(i[5]))
        #对一整个句子进行情感识别
        for ss in short_sentence:
            if ss == '':
                continue
            ss_score = comment_emotion_recogize(ss)
            #对短句进行情感识别

            for actor_name in actor_total_dict:
                if actor_name in ss:
                    if not actor_total_dict[actor_name] in tmp.keys():
                        tmp[actor_total_dict[actor_name]] = ss_score
                    else :
                        if tmp[actor_total_dict[actor_name]] < ss_score:
                            tmp[actor_total_dict[actor_name]] = ss_score

        for j in tmp:
            j_actor_score = tmp[j] * 0.8 + total_score * 0.2
            # 得分加和
            if j in movie_score_dict[movie_id].keys():
                # 演员已有得分情况，则将分数与原有分数相加
                movie_score_dict[movie_id][j] += j_actor_score
            else:
                # 演员未有得分情况，赋给演员此评论得分
                movie_score_dict[movie_id][j] = j_actor_score
                # 将评分赋给演员
    for i in movie_score_dict:

        if movie_score_dict[i] == None:
            continue

        with open("./movie_actor_score_example/" + i + ".json", 'w') as f:
            # 将得分情况以字典形式存入json
            json.dump(movie_score_dict[i], f)
        for j in movie_score_dict[i]:
            print(j, movie_score_dict[i][j])
            # comment_emotion_recogize(ss)