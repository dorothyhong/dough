"""REST API for posts."""
import flask
from flask import session, request, abort
import insta485
from insta485.views.accounts import authenticate, get_old_passwd
from insta485.views.index import get_comments_for_post, get_likes_count
from insta485.views.index import get_user_profile_picture


@insta485.app.route('/api/v1/')
def get_urls():
    """Get urls."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context), 200


# def verify_username_password(username, password, users):
#   return username in users and password == users['password']
def authenticate_helper():
    """Help authenticate posts."""
    if flask.request.authorization:
        username = request.authorization['username']
        password = request.authorization['password']
        return username, password
    if "username" in session:
        username = session['username']
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute("""SELECT password
                       FROM users
                       WHERE username = ?""",
                       (username,))
        password = cursor.fetchone()['password']
        return username, password
    return abort(403)


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_new_posts():
    """Get new posts."""
    username, password = authenticate_helper()

    if (authenticate(username, password) or
       (password == (get_old_passwd(username)['password']))):
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

        context = {}
        context["url"] = current_url

        if size is None:
            size = 10

        if page is None:
            page = 0

        if page < 0 or size <= 0:
            abort(400)

        # Calculate offset for SQL query
        offset = page * size

        connection = insta485.model.get_db()
        cursor = connection.cursor()

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

        context["results"] = []

        for post in posts:
            context["results"].append({
                "postid": post['postid'],
                "url": f"/api/v1/posts/{post['postid']}/"
            })

        # Determine next URL
        context["next"] = ""
        if len(posts) >= size:
            context["next"] = (
                f"/api/v1/posts/?size={size}"
                f"&page={page + 1}"
                f"&postid_lte={postid_lte}"
            )

        return flask.jsonify(**context), 200

    flask.abort(403)


@insta485.app.route('/api/v1/posts/<postid>/', methods=["GET"])
def get_post_detail(postid):
    """Get post details."""
    # Check if basic authorization information is available
    username = ""
    password = ""
    # Check if user is authenticated using HTTP Basic Auth or session cookies
    if flask.request.authorization:
        username = request.authorization['username']
        password = request.authorization['password']
    elif "username" in session:
        username = session['username']
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute("""SELECT password
                       FROM users
                       WHERE username = ?""",
                       (username,))
        password = cursor.fetchone()['password']
        # print(username)
        # print(password)
    else:
        abort(403)  # No authentication credentials provided

    if (authenticate(username, password) or
       (password == (get_old_passwd(username)['password']))):
        connection = insta485.model.get_db()
        cursor = connection.cursor()

        # Check if the post ID exists
        cursor.execute("SELECT postid FROM posts WHERE postid = ?;", (postid,))
        if not cursor.fetchone():
            flask.abort(404)  # Post ID not found

        context = {"comments": []}
        comments = get_comments_for_post(postid)

        for comment in comments:
            owner = comment['owner']
            cid = comment['commentid']
            context["comments"].append({
                "commentid": comment['commentid'],
                "lognameOwnsThis": (comment['owner'] == username),
                "owner": comment['owner'],
                "ownerShowUrl": f"/users/{owner}/",
                "text": comment['text'],
                "url": f"/api/v1/comments/{cid}/"
            })

        # Retrieve the one post based on postid
        cursor.execute("""SELECT filename, owner, created
                       FROM posts
                       WHERE postid = ?;""",
                       (postid,))
        post = cursor.fetchone()
        if post is None:
            flask.abort(404)

        post_owner = post["owner"]

        context.update({
            "comments_url": f"/api/v1/comments/?postid={postid}",
            "created": post["created"],
            "imgUrl": "/uploads/" + post["filename"],
            "owner": post["owner"],
            "ownerImgUrl": "/uploads/" + get_user_profile_picture(post_owner),
            "ownerShowUrl": f"/users/{post_owner}/",
            "postShowUrl": f"/posts/{postid}/",
            "postid": int(postid),
            "url": f"/api/v1/posts/{postid}/"
        })

        # Fetch the like status
        cursor.execute("""SELECT likeid
                       FROM likes
                       WHERE owner = ? AND postid = ?;""",
                       (username, postid))
        like = cursor.fetchone()
        if like:
            l_id = like['likeid']
            url = f"/api/v1/likes/{l_id}/"
        else:
            url = None

        context["likes"] = {
            "lognameLikesThis": like is not None,
            "numLikes": get_likes_count(postid),
            "url": url
        }

        return flask.jsonify(**context), 200

    flask.abort(401)


def get_most_recent_likeid():
    """Get most recent like id."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()

    # Execute the SQL query to find the most recent likeid
    cursor.execute('SELECT MAX(likeid) AS max_likeid FROM likes')
    result = cursor.fetchone()

    # Extract the most recent likeid from the result
    most_recent_likeid = result['max_likeid']

    return most_recent_likeid


@insta485.app.route('/api/v1/likes/', methods=["POST"])
def create_like():
    """Create a like at postid."""
    username = ""
    password = ""
    # Check if user is authenticated using HTTP Basic Auth or session cookies
    if flask.request.authorization:
        username = request.authorization['username']
        password = request.authorization['password']
    elif "username" in session:
        username = session['username']
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute("""SELECT password
                       FROM users
                       WHERE username = ?""",
                       (username,))
        password = cursor.fetchone()['password']
        # print(username)
        # print(password)
    else:
        abort(403)

    postid = flask.request.args.get('postid')
    # Authenticate user
    if (authenticate(username, password) or
       (password == (get_old_passwd(username)['password']))):
        connection = insta485.model.get_db()
        cursor = connection.cursor()

        # Now check if the like exists already
        cursor.execute(
            """
            SELECT likeid FROM likes WHERE owner = ? AND postid = ?;
            """, (username, postid)
        )
        existing_like = cursor.fetchone()

        print("check existing like")
        print(existing_like)

        if existing_like:
            # Like already exists, return the like object
            existing = existing_like['likeid']
            return flask.jsonify({
                "likeid": existing_like['likeid'],
                "url": f"/api/v1/likes/{existing}/"
            }), 200

        print("CHECK: like doesn't exist")

        # use to be else here
        # Create the like
        cursor.execute(
            """
            INSERT INTO likes (owner, postid) VALUES (?, ?);
            """, (username, postid)
        )

        print("insert like")
        print(username)
        print(postid)

        connection.commit()

        # Retrieve the likeid of the newly created like
        likeid = cursor.lastrowid

        print("CHECK likeid")
        print(likeid)

        return flask.jsonify({
            "likeid": likeid,
            "url": f"/api/v1/likes/{likeid}/"
        }), 201
    flask.abort(403)


@insta485.app.route('/api/v1/likes/<likeid>/', methods=["DELETE"])
def remove_like(likeid):
    """Remove like."""
    username = ""
    password = ""
    # Check if user is authenticated using HTTP Basic Auth or session cookies
    if flask.request.authorization:
        username = request.authorization['username']
        password = request.authorization['password']
    elif "username" in session:
        username = session['username']
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute("""SELECT password
                       FROM users
                       WHERE username = ?""",
                       (username,))
        password = cursor.fetchone()['password']
    else:
        abort(403)  # No authentication credentials provided

    if (authenticate(username, password) or
       (password == (get_old_passwd(username)['password']))):

        connection = insta485.model.get_db()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT owner FROM likes WHERE likeid = ?;
            """, (likeid,)
        )

        like_owner = cursor.fetchone()

        if like_owner is None:
            abort(404)
        else:
            if like_owner['owner'] != username:
                abort(403)
            else:
                # delete_like(likeid)
                cursor.execute("""
                    DELETE FROM likes
                    WHERE likeid = ?
                """, (likeid,))
                connection.commit()

                print("delete likeid")
                print(likeid)

        context = {}

        return flask.jsonify(**context), 204
    flask.abort(403)


@insta485.app.route('/api/v1/comments/', methods=["POST"])
def create_comment():
    """Create comment."""
    username = ""
    password = ""
    # Check if user is authenticated using HTTP Basic Auth or session cookies
    if flask.request.authorization:
        username = request.authorization['username']
        password = request.authorization['password']
    elif "username" in session:
        username = session['username']
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute("""SELECT password
                       FROM users
                       WHERE username = ?""",
                       (username,))
        password = cursor.fetchone()['password']
        # print(username)
        # print(password)
    else:
        abort(403)

    if (authenticate(username, password) or
       (password == (get_old_passwd(username)['password']))):
        text = flask.request.json.get("text", None)
        postid = flask.request.args.get('postid')

        connection = insta485.model.get_db()
        cursor = connection.cursor()

        # Check if the post ID exists
        cursor.execute("SELECT postid FROM posts WHERE postid = ?;", (postid,))
        if cursor.fetchone() is None:
            flask.abort(404)

        cursor.execute("""
            INSERT INTO comments (owner, postid, text, created)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (username, postid, text))

        cursor.execute('SELECT MAX(commentid) AS max_commentid FROM comments')
        result = cursor.fetchone()
        most_recent_commentid = result['max_commentid']

        context = {
            "commentid": most_recent_commentid,
            "lognameOwnsThis": True,
            "owner": username,
            "ownerShowUrl": f"/users/{username}/",
            "text": text,
            "url": f"/api/v1/comments/{most_recent_commentid}/"
        }

        return flask.jsonify(**context), 201

    flask.abort(403)


@insta485.app.route('/api/v1/comments/<commentid>/', methods=["DELETE"])
def delete_comment(commentid):
    """Delete comment."""
    # Check if basic authorization information is available
    username = ""
    password = ""
    # Check if user is authenticated using HTTP Basic Auth or session cookies
    if flask.request.authorization:
        username = request.authorization['username']
        password = request.authorization['password']
    elif "username" in session:
        username = session['username']
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute("""SELECT password
                       FROM users
                       WHERE username = ?""",
                       (username,))
        password = cursor.fetchone()['password']
        # print(username)
        # print(password)
    else:
        abort(403)  # No authentication credentials provided

    if (authenticate(username, password) or
       (password == (get_old_passwd(username)['password']))):
        connection = insta485.model.get_db()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT owner FROM comments WHERE commentid = ?;
            """, (commentid)
        )
        comment_owner = cursor.fetchone()

        if comment_owner is None:
            abort(404)
        else:
            if comment_owner["owner"] != username:
                abort(403)
            else:
                cursor.execute("""
                    DELETE FROM comments
                    WHERE commentid = ?
            """, (commentid,))

            context = {}

            return flask.jsonify(**context), 204
    flask.abort(403)
