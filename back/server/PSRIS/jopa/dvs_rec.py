import json
import scipy as sp
import numpy as np
import os
from random import shuffle
from sklearn.metrics.pairwise import cosine_similarity
from jopa.VkApi import VkApi
import requests
from time import sleep


class dvs_model:
    __instance = None

    def __new__(cls, *args, **kwargs):
        # if not cls.__instance:
        cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self,matrix, dir:str='jopa/DVS and VVRIS/time data and backups/'):
        self.similar_pubs={}
        self.similar_users={}

        self.pub_posts = {}

        self.matrix = sp.sparse.load_npz(matrix)
        self.Vk= VkApi(load=False)

        with open(dir + 'users_id.json') as file:
            self.user_id = json.load(file)
        self.id_user = {}

        for item in self.user_id.items():
            self.id_user[item[1]] = item[0]

        with open(dir + 'pubs_id.json') as file:
            self.pubs_id = json.load(file)
        self.id_pubs = {}

        for item in self.pubs_id.items():
            self.id_pubs[item[1]] = item[0]


        with open(dir + 'similar_pubs.json') as file:
            self.similar_pubs = json.load(file)

        with open(dir + 'similar_users.json') as file:
            self.similar_users = json.load(file)

        try:
            with open(dir + 'pub_post.json') as file:
                self.pub_posts = json.load(file)
        except:
            self.pub_posts = {}

    def get_free_id(self):
        return self.matrix.shape[1]

# когда создается новый чел
    def add_rc(self):
        shape = self.matrix.shape
        self.matrix = self.matrix.resize(shape[0]+1,shape[1]+1)

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

        return res_pubs

    def get_most_liked(self,user,all=False,top=10):
        if type(user) == str:
            user = int(user)

        interaction_ids = self.matrix[user].nonzero()[1]
        if len(interaction_ids):
            interaction_vals = self.matrix[user,interaction_ids].todense().tolist()[0]
            inters_list = list(zip(interaction_vals,interaction_ids))
            # print(inters_list)
            if all:
                return sorted(inters_list,key = lambda x:x[0])
            else:
                return sorted(inters_list, key=lambda x: x[0])[-top:]
        return None

    def calculate_similar(self,pub=None,user=None,simple =False):
        if not (pub or user):
            raise ValueError("pub and user are None")
        elif pub:
            col = self.matrix[:,pub]
            # print(col.shape)
            # similarity_list = []
            # v1_sq = col.T.dot(col)[0,0]
            similarity_list = list(cosine_similarity(col.T, self.matrix.transpose())[0])
            similarity_list = list(map(float,similarity_list))
            similarity_list = zip(similarity_list,range(col.shape[0]))
            similar = {index:value for value,index in sorted(similarity_list,key=(lambda x:x[0]))[-6:-1]}
            self.similar_pubs[int(pub)] = similar
        else:
            row = self.matrix[user]
            # print(col.shape)
            # similarity_list = []
            # v1_sq = col.T.dot(col)[0,0]
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

    def p_predict(self,id_p):
        index_pr = [(indx,pr) for indx,pr in id_p.items()]
        index_pr = sorted(index_pr,key=lambda x:x[1])
        probs = [i[1] for i in index_pr]

        probs = np.array(probs,dtype=np.float64)
        probs /= np.sqrt(probs.T@probs)
        val = np.random.uniform(0,sum(probs),size=(1,))[0]

        if 0<val<probs[-1]:
            return index_pr[-1][0]
        elif probs[-1:]<val<sum(probs[-2:]):
            return index_pr[-2][0]
        elif sum(probs[-2:])<val<sum(probs[-3:]):
            return index_pr[-3][0]
        elif sum(probs[-3:])<val<sum(probs[-4:]):
            return index_pr[-4][0]
        elif sum(probs[-4:])<val<sum(probs[-5:]):
            return index_pr[-5][0]

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

    def save_state(self,dir:str='DVS and VVRIS/time data and backups/'):
        for item in self.pubs_id.items():
            self.id_pubs[item[1]] = item[0]

        with open(dir + 'similar_pubs.json','w') as file:
            json.dump(self.similar_pubs, file)

        with open(dir + 'similar_users.json','w') as file:
             json.dump(self.similar_users, file)

        with open(dir + 'pub_post.json','w') as file:
             json.dump(self.pub_posts, file)

    def get_and_save_posts(self,pubs:list[int],dir_profile:str,dir_posts:str):
        """pubs are out inner ids"""
        freshed = []
        if dir_profile[-1] != '/':
            dir_profile = dir_profile + '/'
        if dir_posts[-1] != '/':
            dir_posts = dir_posts+'/'
        new_pubs = []
        for pub in pubs:
            if pub not in self.pub_posts.keys():
                new_pubs.append(pub) # vk ids for parsing
        # print(new_pubs)
        new_pubs_vk = [self.id_pubs[pub] for pub in new_pubs]

        new_info_pubs = self.Vk.get(method='groups.getById',access_token=self.Vk.pr_access_token,group_ids=', '.join(new_pubs_vk),v=self.Vk.v)['response'] # getting these pubs

        # for inf_pub in info_pubs:
        #     inf_ids = inf_pub['id']
        #
        # print(len(new_pubs),len(info_pubs))
        # print([i for i in zip(new_pubs,info_pubs)])
        avatars = os.listdir(dir_profile)
        for info in new_info_pubs:
            #getting name
            name = info['photo_100'].replace('//', '/')
            name = name.split('/')
            name = name[-1]
            if name.find('?') != -1:
                name = name[:name.find('?')]
            print(name)
            print(len(name))
            name = name[:25] + ".jpg"
            print(name)
            print(len(name))

            #making json
            self.pub_posts[self.pubs_id[str(info['id'])]] = {'username': info['name'], 'innner_id': self.pubs_id[str(info['id'])], 'outer_id': info['id'],'image_name':name,
                                          'image_url': info['photo_100'],'posts':[]}
            if info['photo_100'] not in avatars:
                img = requests.get(info['photo_100'])

            with open(dir_profile+name, 'wb') as im_file:
                im_file.write(img.content)
                sleep(0.3)

        print('pub_post!!!!\n',self.pub_posts.keys(),'\n')

        for pub in pubs:
            if pub not in freshed:
                freshed.append(pub)
                if pub in self.pub_posts.keys():
                    old_posts = self.pub_posts[int(pub)]['posts']
                else:
                    old_posts = []
                fresh_posts = self.Vk.get_posts(int(self.id_pubs[int(pub)]))
                new_posts = []
                if fresh_posts:
                    for post in fresh_posts:
                        if post not in old_posts:
                            new_posts.append(post)
                    self.Vk.save_images(dir_posts,new_posts)
                    try:
                        self.pub_posts[int(pub)]['posts'] = new_posts + old_posts
                        print("saved!")
                    except:
                        pass
        #
        #
