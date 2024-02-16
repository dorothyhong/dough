"""REST API for posts."""
import flask
from flask import session, request, abort
import insta485
from insta485.views.accounts import authenticate, verify_password
from insta485.views.post_req import add_like
from insta485.views.index import get_like_status


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

from flask import request

@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_new_posts():
    username = request.authorization['username']
    password = request.authorization['password']

    
    if authenticate(username, password):
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        
        # Get parameters from request
        size = request.args.get('size', type=int)
        page = request.args.get('page', type=int)
        postid_lte = request.args.get('postid_lte', type=int)

        
        # Construct the current URL
        current_url = "/api/v1/posts/"
        if size is not None or page is not None or postid_lte is not None:
            current_url += "?"
            params = []
            if size is not None:
                params.append(f"size={size}")
            if page is not None:
                params.append(f"page={page}")
            if postid_lte is not None:
                params.append(f"postid_lte={postid_lte}")
            current_url += "&".join(params)
            
        if size is None:
            size = 10
        elif size <= 0:
            abort(400)
        
        if page is None:
            page = 0
        elif page < 0:
            abort(400)
            
        
        # Calculate offset for SQL query
        offset = page * size

        # Retrieve the most recent postid for default postid_lte
        if postid_lte is None:
            cursor.execute('SELECT MAX(postid) as max_postid FROM posts')
            most_recent_post = cursor.fetchone()
            postid_lte = most_recent_post['max_postid']

        # Query for the posts based on provided filters
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
        posts = cursor.fetchall()

        context = {}
        context["results"] = []

        for post in posts:
            context["results"].append({"postid": post['postid'], "url": f"/api/v1/posts/{post['postid']}/"})

        # Determine next URL
        if len(posts) < size:
            next_url = ""
        else:
            last_postid = posts[-1]['postid']
            next_url = f"/api/v1/posts/?size={size}&page={page + 1}&postid_lte={postid_lte}"

        context["url"] = current_url
        context["next"] = next_url

        return flask.jsonify(**context), 200

    flask.abort(403)


@insta485.app.route('/api/v1/posts/<postid>/', methods=["GET"])
def get_post_detail(postid):
    username = request.authorization['username']
    password = request.authorization['password']

    
    if authenticate(username, password):
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        
        # Check if the post ID exists
        cursor.execute(
            """
            SELECT postid FROM posts WHERE postid = ?;
            """, (postid,)
        )
        if not cursor.fetchone():
            flask.abort(404)  # Post ID out of range
            
            
            
            
            
        
    
    
def get_most_recent_likeid():
    connection = insta485.model.get_db()  # Get the database connection
    cursor = connection.cursor()  # Create a cursor object

    # Execute the SQL query to find the most recent likeid
    cursor.execute('SELECT MAX(likeid) AS max_likeid FROM likes')
    result = cursor.fetchone()  # Fetch the result

    # Extract the most recent likeid from the result
    most_recent_likeid = result['max_likeid']
    
    return most_recent_likeid

    
@insta485.app.route('/api/v1/likes/', methods=["POST"])
def create_like():
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    postid = flask.request.args.get('postid')

    if not authenticate(username, password):
        flask.abort(403)  # Authentication failed

    connection = insta485.model.get_db()
    cursor = connection.cursor()

    # Now check if the like exists already
    cursor.execute(
        """
        SELECT likeid FROM likes WHERE owner = ? AND postid = ?;
        """, (username, postid)
    )
    existing_like = cursor.fetchone()
    
    if existing_like:
        # Like already exists, return the like object
        return flask.jsonify({
            "likeid": existing_like['likeid'],
            "url": f"/api/v1/likes/{existing_like['likeid']}/"
        }), 200
    else:
        # Create the like
        cursor.execute(
            """
            INSERT INTO likes (owner, postid) VALUES (?, ?);
            """, (username, postid)
        )
        connection.commit()
        
        # Retrieve the likeid of the newly created like
        likeid = cursor.lastrowid
        
        return flask.jsonify({
            "likeid": likeid,
            "url": f"/api/v1/likes/{likeid}/"
        }), 201  # Return a 201 status code for Created
    
def delete_like(likeid):
    """Post remove like."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM likes
        WHERE likeid = ?
    """, (likeid))


@insta485.app.route('/api/v1/likes/<likeid>/', methods=["DELETE"])
def remove_like(likeid):
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']

    if not authenticate(username, password):
        flask.abort(403)  # Authentication failed
        
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT owner FROM likes WHERE likeid = ?;
        """, (likeid)
    )
    like_owner = cursor.fetchone()['owner']
    
    if like_owner != username:
        abort(403)
    elif like_owner is None:
        abort(404)
    else:
        delete_like(likeid)

    context = {}

    return flask.jsonify(**context), 204
    
@insta485.app.route('/api/v1/comments/?postid=<postid>', methods=["POST"])
def create_comment(postid):
    
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    text = flask.request.args.get('text')

    connection = insta485.model.get_db()
    cursor = connection.cursor()

     # Check if the post ID exists
    cursor.execute(
        """
        SELECT postid FROM posts WHERE postid = ?;
        """, (postid,)
    )
    if not cursor.fetchone():
        flask.abort(404)  # Post ID out of range

        
    cursor.execute("""
        INSERT INTO comments (owner, postid, text, created)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (username, postid, text))
    
    cursor = connection.cursor()  # Create a cursor object
    
    cursor.execute('SELECT MAX(commentid) AS max_commentid FROM comments')
    result = cursor.fetchone()  # Fetch the result

    most_recent_commentid = result['max_commentid']

    context = {
    "commentid": most_recent_commentid,
    "lognameOwnsThis": True,
    "owner": username,
    "ownerShowUrl": "/users/" + username + "/",
    "text": text,
    "url": "/api/v1/comments/" + most_recent_commentid + "/"
    }

    return flask.jsonify(**context), 201

@insta485.app.route('/api/v1/comments/<commentid>/', methods=["DELETE"])
def delete_comment(commentid):
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']

    if not authenticate(username, password):
        flask.abort(403)  # Authentication failed
        
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT owner FROM likes WHERE commentid = ?;
        """, (commentid)
    )
    like_owner = cursor.fetchone()['owner']
    
    if like_owner != username:
        abort(403)
    elif like_owner is None:
        abort(404)
    else:
        cursor.execute("""
                DELETE FROM comments
                WHERE commentid = ?
        """, (commentid,))

    context = {}

    return flask.jsonify(**context), 204
    
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