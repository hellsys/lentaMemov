import math
import requests
import json
import time
import os

class VkApi:
    __url = 'https://api.vk.com/method/'
    methods = ("groups.getMembers",'users.get','users.getSubscriptions')
    v = 5.131
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self,load = True):
        if getattr(self.__instance, "access_token", None) is None:
            self.pr_access_token = 'a51b889aa51b889aa51b889afca60aadc3aa51ba51b889ac649366d7024d770fb205856'
        if load:
            self.new_users = []
            self.new_groups = []
            self.usr_pub = {}
            self.pub_user = {}
            try:
                with open('pub_user.json') as file:
                    self.pub_user =  json.load(file)
                with open('user_pub.json') as file:
                    self.usr_pub = json.load(file)
            except BaseException:
                self.pub_user = {}
                self.usr_pub = {}

    def dump(self,**kwargs):
        if 'users' in kwargs.keys():
            users = kwargs['users']
            with open('users.txt','a') as file:
                for i in range(math.ceil(len(users)//50)):
                    users_to_write = list(map(str,users[i*50:(i+1)*50]))
                    string = ' '.join(users_to_write) + '\n'
                    file.write(string)

        if 'groups' in kwargs.keys():
            groups = kwargs['groups']
            with open('groups.txt', 'w+') as file:
                for i in range(math.ceil(len(groups) // 50)):
                    groups_to_write = list(map(str,groups[i * 50:(i + 1) * 50]))
                    string = ' '.join(groups_to_write) + '\n'
                    file.write(string)
        if 'user_pub' in kwargs.keys():
            user_pub = kwargs['user_pub']
            with open('user_pub.json', 'w+') as file:
                json.dump(user_pub,file,indent=2)

        if 'pub_user' in kwargs.keys():
            pub_user = kwargs['pub_user']
            with open('pub_user.json','w+') as file:
                json.dump(pub_user, file,indent=2)

    def get(self,method:str,**kwargs):
        request = self.__url+method+'?'
        for i in kwargs:
            request = f'{request}{i}={kwargs[i]}&'
        request = request[:-1]  # обрубаем последний &
        return requests.get(request).json()

    def user_is_private(self,user):
        user_id = user
        response = self.get('users.get', access_token=self.pr_access_token, user_id=user_id, v=self.v)
        return self.__check_user(response)

    def get_user_id(self,user_id:str):
        response = self.get('users.get', access_token=self.pr_access_token, user_id=user_id, v=self.v)
        return str(response['response'][0]['id'])

    @staticmethod
    def __check_user(data):
        if len(data['response']) == 0:
            return True #
        if 'deactivated' in data['response'][0].keys():
            return True
        res = data['response'][0]['is_closed']
        return res

    def get_subs(self,user):
        if isinstance(user, int):
            user_id = self.users[user]
        else:
            user_id = user
        subs = None
        try:
            if not self.user_is_private(user_id):
                response = self.get('users.getSubscriptions', access_token=self.pr_access_token, user_id=user_id, v=self.v)
                subs = response['response']['groups']['items']
        except Exception as ex:
            print(ex.args)
        return subs

    def get_group_subs(self,group,amount=None):
        response = self.get('groups.getMembers', access_token=self.pr_access_token, group_id=group, v=self.v)
        # print(group,'\n')
        if self.__check_group(response):
            return None
        sub_quantity = response['response']['count']

        if sub_quantity > 10000:
            sub_quantity = (6500 + int(sub_quantity*0.3))%sub_quantity

        subs = response['response']['items']
        for i in range(math.ceil(sub_quantity/1000)-1):
            response = self.get('groups.getMembers', offset=1000*(i+1), access_token=self.pr_access_token, group_id=group, v=self.v)
            for sub in response['response']['items']:
                subs.append(sub)
            time.sleep(0.4)
        return subs

    @staticmethod
    def __check_group(data):
        return 'error' in data.keys()

    def parse(self,iterations=1000):
        for user in self.users[:16]:
            if user not in self.usr_pub.keys():
                subs = self.get_subs(user)
                self.usr_pub[user] = subs
                if subs:
                    for sub in subs:
                        if sub not in self.pub_user.keys():
                            self.new_groups.append(sub)
                time.sleep(0.4)

        for group in self.new_groups[:16]:
            if group not in self.pub_user.keys():
                subs = self.get_group_subs(group)
                self.pub_user[group] = subs
                if subs:
                    for sub in subs:
                        if sub not in self.usr_pub.keys():
                            self.new_users.append(sub)
                time.sleep(0.4)

        self.dump(users=self.new_users,groups=self.new_groups,user_pub=self.usr_pub,pub_user=self.pub_user)

    def get_posts(self, pub:int, count=10):

        """returns posts from the pub\n
        pub:int - id of the pub"""
        reply = self.get('wall.get',access_token = self.pr_access_token,owner_id =str(-pub),v=self.v)
        if 'error' in reply.keys():
            return None
        posts = reply['response']['items'][:count]
        res_posts = []
        for i,post in enumerate(posts):
            # print(post)
            # print()
            post_res = {'text': post['text'],'likes': post['likes']['count'],
                        'img_names': [], 'img_urls': []}
            if 'views' in post.keys():
                post_res['views'] = post['views']['count']
            else:
                post_res['views'] = 0
            if 'attachments' in post.keys():
                for attachment in post['attachments']:
                    if attachment['type'] == 'photo':
                        attachment = attachment['photo']
                        image_sizes = attachment['sizes']
                        image_sizes = sorted(image_sizes, key=lambda x: x['height'])
                        for img in image_sizes[::-1]:
                            if img['height'] < 340:
                                post_res['img_urls'].append(img['url'])
                                name = img['url'].replace('//', '/')
                                name = name.split('/')
                                name = name[-1]
                                name = name[:name.find('?')]
                                post_res['img_names'].append(name)
                                break
            if len(post_res['text']) or len(post_res['img_names']):
                res_posts.append(post_res)
        return res_posts

    def save_images(self,dir:str,posts):
        """Saves images from posts into dir:\n
        example: pubs/POTS/images"""
        pictures =  os.listdir(dir)
        for i in posts:
            for url,name in zip(i['img_urls'],i['img_names']):
                if name not in pictures:
                    img = requests.get(url)
                    with open(dir+name, 'wb') as im_file:
                        im_file.write(img.content)
                        time.sleep(0.3)#

    def get_and_save_posts(self,pubs:list[int]):
        for pub in pubs:
            self.get_posts(pub)

