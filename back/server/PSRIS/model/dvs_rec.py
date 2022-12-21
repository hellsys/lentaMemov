import json
import scipy as sp
import numpy as np
import os
from random import shuffle
from sklearn.metrics.pairwise import cosine_similarity
import requests
from time import sleep


class dvs_model:
    __instance = None

    def __new__(cls, *args, **kwargs):
        # if not cls.__instance:
        cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self,matrix, dir:str='model/data/'):
        self.similar_pubs={}
        self.similar_users={}

        self.pub_posts = {}

        self.matrix = sp.sparse.load_npz(matrix)

        with open(dir + 'users_id.json') as file:
            self.user_id = json.load(file)
        self.id_user = {}

        for item in self.user_id.items():
            self.id_user[item[1]] = item[0]


        with open(dir + 'similar_pubs.json') as file:
            self.similar_pubs = json.load(file)

        with open(dir + 'similar_users.json') as file:
            self.similar_users = json.load(file)

        try:
            with open(dir + 'pub_post.json') as file:
                self.pub_posts = json.load(file)
        except:
            self.pub_posts = {}
    
    def get_shape(self):
        return self.matrix.shape

# когда создается новый чел
    def add_rc(self):
        shape = self.matrix.shape
        self.matrix.resize(shape[0]+1,shape[1]+1)
        print(self.matrix.shape)

# Добавление взаимодействия
    def add_interation(self,usr_pub:dict):
        self.matrix[usr_pub['user']]*=0.9
        self.matrix[usr_pub['user'],usr_pub['pub']]+=1

# возвращает айдишники пабликов
    def get_recommendations(self,user):
        most_liked = self.get_most_liked(user,top=10)

        similar_users = self.get_similar_users(str(user))

        most_liked_by_others = []

        for sim_user in similar_users.keys():
            most_liked_by_others.append(self.get_most_liked(sim_user))

        similar_pubs = []

        for m_pub in most_liked:
            similar_pubs.append(self.get_similar_pubs(m_pub[1]))

        # top_10_pubs =
        res_pubs = []
        for sim_pubs in similar_pubs:
            res_pubs += sim_pubs.keys()
        for mlbo in most_liked_by_others:
            res_pubs += [i[1] for i in mlbo]

        # mixing top
        ###

        shuffle(res_pubs)
        res_pubs = [i[1] for i in most_liked] + res_pubs

        for i in range(len(res_pubs)):
            if len(res_pubs) <= i:
                break
            if res_pubs.count(res_pubs[i]) >2:
                res_pubs.pop(i)
        res_pubs += [np.random.randint(1,self.matrix.shape[1]) for i in range(30-len(res_pubs))]
        return res_pubs 

    def get_most_liked(self,user,all=False,top=10):
        if type(user) == str:
            user = int(user)

        interaction_ids = self.matrix[user].nonzero()[1]
        if len(interaction_ids):
            interaction_vals = self.matrix[user,interaction_ids].todense().tolist()[0]
            inters_list = list(zip(interaction_vals,interaction_ids))
            if all:
                return sorted(inters_list,key = lambda x:x[0])
            else:
                return sorted(inters_list, key=lambda x: x[0])[-top:]
        return None

    def calculate_similar(self,pub=None,user=None,simple =False):
        if not (pub is not None or user is not None):
            raise ValueError("pub and user are None")
        elif pub is not None:
            col = self.matrix[:,pub]
            similarity_list = list(cosine_similarity(col.T, self.matrix.transpose())[0])
            similarity_list = list(map(float,similarity_list))
            similarity_list = zip(similarity_list,range(col.shape[0]))
            similar = {index:value for value,index in sorted(similarity_list,key=(lambda x:x[0]))[-6:-1]}
            self.similar_pubs[int(pub)] = similar
        else:
            row = self.matrix[user]
            similarity_list = list(cosine_similarity(row, self.matrix)[0])
            similarity_list = list(map(float, similarity_list))
            similarity_list = zip(similarity_list, range(row.shape[1]))
            similar = {index: value for value, index in sorted(similarity_list, key=(lambda x: x[0]))[-6:-1]}
            self.similar_users[int(user)] = similar

    @staticmethod
    def calc_similarity_subprocess(col,matrix):
        similarity_list = list(cosine_similarity(col.T, matrix.transpose())[0])
        similarity_list = list(map(float, similarity_list))
        similarity_list = zip(similarity_list, range(col.shape[0]))
        similar = {index: value for value, index in sorted(similarity_list, key=(lambda x: x[0]))[-6:-1]}
        return similar

    def get_similar_pubs(self,pub,recalculate = False):
        #special json for that
        if recalculate:
            self.calculate_similar(pub)
        if pub not in self.similar_pubs.keys():
            self.calculate_similar(pub)
        return self.similar_pubs[pub]

    def get_similar_users(self,user,recalculate = False):
        if type(user) == str:
            user = int(user)
        #special json for that
        if recalculate:
            self.calculate_similar(user=user)
        if user not in self.similar_users.keys():
            self.calculate_similar(user=user)
        return self.similar_users[user]

    def get_best_pubs(self,user,amount = 5):
        most_liked_ids = self.get_most_liked(user,top=5)
        similar_pubs = []
        for indx in most_liked_ids:
            similar_pubs.append(self.get_similar_pubs(indx))

    def save_state(self,dir:str='jopa/DVS and VVRIS/time data and backups/'):

        with open(dir + 'similar_pubs.json','w') as file:
            json.dump(self.similar_pubs, file)

        with open(dir + 'similar_users.json','w') as file:
             json.dump(self.similar_users, file)

        sp.sparse.save_npz(dir + 'cutted_m.npz', self.matrix)
