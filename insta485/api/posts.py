"""REST API for posts."""
import flask
from flask import session
import insta485


@insta485.app.route('/api/v1/')
def get_urls():
  context = {
    "comments": "/api/v1/comments/",
    "likes": "/api/v1/likes/",
    "posts": "/api/v1/posts/",
    "url": "/api/v1/"
  }
  return flask.jsonify(**context), 200


def verify_username_password(username, password):
  return username in users and password == users['password']


@insta485.app.route('/api/v1/posts/')
def get_new_posts():
  
  auth = flask.request.authorization

  """Get 10 recent posts."""
  if not auth:
    username = session["username"]
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute(
      """
        SELECT postid, filename, owner, created
        FROM posts
        WHERE owner = ? OR owner IN
        (SELECT username2 FROM following WHERE username1 = ?)
        ORDER BY postid DESC
        LIMIT 10;
    """, (username, username,))
    posts = cursor.fetchall()
    connection = insta485.model.close_db("error")
  elif auth:
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    verify_username_password(username, password)
    
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    cursor2.execute(
      """
        SELECT username
        FROM users
        WHERE userame = ?
      """, (username))
    
  
    cursor.execute(
      """
        SELECT postid, filename, owner, created
        FROM posts
        WHERE owner = ? OR owner IN
        (SELECT username2 FROM following WHERE username1 = ?)
        ORDER BY postid DESC
        LIMIT 10;
    """, (username, username,))
    posts = cursor.fetchall()
    connection = insta485.model.close_db("error")
    users = cursor2.fetchall()  
    return flask.jsonify(**posts), 200
  flask.abort(403)
  
  
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
