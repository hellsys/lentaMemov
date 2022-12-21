import json
from lenta.models import Post, PostImage
from account.models import Profile
from django.contrib.auth.models import User
from tqdm import tqdm


with open('pub_post.json', 'r') as user_json:
    user_json_read = json.load(user_json)
    for user in tqdm(user_json_read.values()):
        id = user['innner_id']
        username = user['username']
        if user['image_name']:
            image = f"profile_pics/{user['image_name']}"
        user_ = User(id=id, username=username)
        user_.save()
        profile = Profile(image=image, user_id=user_.id)
        profile.save()
        posts = user['posts']
        for post in posts:
            content = post['text']
            author_id = id
            post_ = Post(content=content, author_id = author_id)
            post_.save()
            if post['img_names']:
                for image in post['img_names']:
                    image_ = PostImage(image=f"post_pics/{image}", post_id=post_.id)
                    image_.save()

