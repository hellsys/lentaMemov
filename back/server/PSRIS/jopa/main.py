import json

root = 'DVS and VVRIS/time data and backups/'
#
# with open(root+'users_id.json') as file:
#     user_id = json.load(file)
# with open(root + 'pubs_id.json') as file:
#     pubs_id = json.load(file)

from dvs_rec import dvs_model

# p_fp = open(root+'pub_similar.json',)
# u_fp = open(root+'user_similar.json',)
dm = dvs_model(root + 'matrix small.npz')   #,p_fp,u_fp)
recs = dm.get_recommendations(dm.user_id['262146191'])
dm.get_and_save_posts(recs,'profile', 'posts')
#
dm.save_state(root)
m = '195414116'
# print(dm.pub_posts.keys(),'\n')
# print('vk.com/public'+ str(dm.id_pubs[2524]))
# print(dm.pub_posts[2524])