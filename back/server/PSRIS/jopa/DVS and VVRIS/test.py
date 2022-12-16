import json

with open('./time data and backups/pub_post.json', 'r') as user_json:
    user_json_read = json.load(user_json)
    for user in user_json_read.values():
        id = user['inner_id']
        username = user['username']
        if user['image_name']:
            image = f"profile/{user['image_name']}"
        user_ = User(id=id, username=username)
        user_.save()
        profile = Profile(image=image, user_id=user_.id)
        posts = user['posts']
        for post in posts:
            content = post['text']
            author_id = id
            post_ = Post(content=content, author_id = author_id)
            post_.save()
            if post['img_names']:
                for image in img_names:
                    image_ = PostImage(image=f"post_pics/{image}", post_id=post_.id)
                    image_.save()

