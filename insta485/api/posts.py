"""REST API for posts."""
import flask
from flask import session
import insta485
from insta485.views.accounts import authenticate, verify_password


@insta485.app.route('/api/v1/')
def get_urls():
  context = {
    "comments": "/api/v1/comments/",
    "likes": "/api/v1/likes/",
    "posts": "/api/v1/posts/",
    "url": "/api/v1/"
  }
  return flask.jsonify(**context), 200


# def verify_username_password(username, password, users):
#   return username in users and password == users['password']



@insta485.app.route('/api/v1/posts/')
def get_new_posts():
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    
    if authenticate(username, password):
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT postid
            FROM posts
            WHERE owner = ? OR owner IN
            (SELECT username2 FROM following WHERE username1 = ?)
            ORDER BY postid DESC
            LIMIT 10;
            """, (username, username,))
        posts = cursor.fetchall()

        context = {}
        context["results"] = []
        context["url"] = "/api/v1/posts/"
        
        postid_lte = flask.request.args.get('postid_lte')
        size = flask.request.args.get('size')
        page = flask.request.args.get('page')
        
        if postid_lte is None:
            postid_lte = len(posts)
            
        if size is None:
            size = len(posts)
        
        # num_pages = floor(len(posts) / size)
        
        if page is None:
            page = 0

        if page is not None:
            index = int(page) * int(size)

        # posts[index + count - 1]
        count = 1
        for post in posts:
            if page is None:
                postid = post['postid']
                if postid <= int(postid_lte) and count <= int(size):
                    context["results"].append({"postid": postid, "url": f"/api/v1/posts/{postid}/"})
            else:
                if index < len(posts):
                    postid = posts[index + count - 1]['postid']
                    if postid <= int(postid_lte) and count <= int(size):
                        context["results"].append({"postid": postid, "url": f"/api/v1/posts/{postid}/"})
            count += 1

        if len(posts) < 10:
            context["next"] = ""
        else:
            last_postid = posts[-1]['postid']
            context["next"] = f"/api/v1/posts/?size=10&page=1&postid_lte={last_postid}"

        return flask.jsonify(**context), 200

    flask.abort(403)

# page 1
# size 3
# 3 posts

  
# def get_posts(query, params):
#     """Get the p."""
#     connection = insta485.model.get_db()
#     cursor = connection.cursor()
#     cursor.execute(query, params)
#     posts = cursor.fetchall()
#     connection = insta485.model.close_db("error")
#     return posts


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid.

    Example:
    {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postShowUrl": "/posts/1/",
      "postid": 1,
      "url": "/api/v1/posts/1/"
    }
    """
    context = {
        "created": "2017-09-28 04:33:28",
        "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": flask.request.path,
    }
    return flask.jsonify(**context)
