"""REST API for posts."""
import flask
from flask import session, request
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
        
        # Get parameters from request
        postid_lte = flask.request.args.get('postid_lte', type=int)
        size = flask.request.args.get('size', default=10, type=int)
        page = flask.request.args.get('page', default=0, type=int)

        # Validate page and size parameters
        if page is None or page < 0:
            flask.abort(400)
        if size <= 0:
            flask.abort(400)

        # Calculate offset for SQL query
        offset = page * size
        

    #     query = """
    #     SELECT postid
    #     FROM posts
    #     WHERE owner = ? OR owner IN
    #     (SELECT username2 FROM following WHERE username1 = ?)
    #     ORDER BY postid DESC;
    # """

        # Build SQL query based on whether postid_lte is provided
        if postid_lte is not None:
            cursor.execute(
                """
                SELECT postid
                FROM posts
                WHERE (owner = ? OR owner IN
                (SELECT username2 FROM following WHERE username1 = ?))
                AND postid <= ?
                ORDER BY postid DESC
                LIMIT ? OFFSET ?;
                """, (username, username, postid_lte, size, offset,))
        else:
            cursor.execute(
                """
                SELECT postid
                FROM posts
                WHERE owner = ? OR owner IN
                (SELECT username2 FROM following WHERE username1 = ?)
                ORDER BY postid DESC
                LIMIT ? OFFSET ?;
                """, (username, username, size, offset,))
        posts = cursor.fetchall()
        print(posts)

        context = {}
        context["results"] = []
        context["url"] = "/api/v1/posts/"

        for post in posts:
            context["results"].append({"postid": post['postid'], "url": f"/api/v1/posts/{post['postid']}/"})

        # Determine next URL
        if len(posts) < size:
            context["next"] = ""
        else:
            last_postid = posts[-1]['postid']
            context["next"] = f"/api/v1/posts/?size={size}&page={page + 1}&postid_lte={last_postid}"

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

# @insta485.app.route('/api/v1/posts/<postid>/')
# def get_post_detial():
    


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
