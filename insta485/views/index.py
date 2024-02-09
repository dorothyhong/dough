"""Deal with Homepage."""
import os
import flask
from flask import session, abort, send_from_directory, render_template
import arrow
import insta485


@insta485.app.route('/')
def show_index():
    """Show index."""
    if "username" in session:
        logged_in_user = session["username"]
        posts = get_recent_posts(logged_in_user)
        context = {"logname": logged_in_user, "posts": []}

        for post in posts:
            post_data = {
                "postid": post["postid"],
                "timestamp": arrow.get(post["created"]).humanize(),
                "owner": post["owner"],
                "likes": get_likes_count(post["postid"]),
                "comments": get_comments_for_post(post["postid"]),
                "img_url": '/uploads/' + post["filename"],
                "owner_img_url": '/uploads/' +
                get_user_profile_picture(post["owner"]),
                "is_liked": get_like_status(post["postid"], logged_in_user)
            }
            context["posts"].append(post_data)

        return flask.render_template("index.html", **context)

    return flask.redirect(flask.url_for('show_login'))


def get_like_status(postid, user):
    """Get like status."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT likeid
        FROM likes
        WHERE postid = ? AND owner = ?
    """, (postid, user,))
    row = cursor.fetchone()
    connection = insta485.model.close_db("error")
    if row is None:
        return False
    return True


def get_recent_posts(user):
    """Get recent posts."""
    query = """
        SELECT postid, filename, owner, created
        FROM posts
        WHERE owner = ? OR owner IN
        (SELECT username2 FROM following WHERE username1 = ?)
        ORDER BY postid DESC;
    """
    return get_posts(query, (user, user))


# def get_recent_posts(user):
#     """Get recent posts."""
#     connection = insta485.model.get_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         SELECT postid, filename, owner, created
#         FROM posts
#         WHERE owner = ? OR owner IN
#         (SELECT username2 FROM following WHERE username1 = ?)
#         ORDER BY postid DESC;
#     """, (user, user))
#     posts = cursor.fetchall()
#     connection = insta485.model.close_db("error")
#     return posts

def get_posts(query, params):
    """Get the p."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute(query, params)
    posts = cursor.fetchall()
    connection = insta485.model.close_db("error")
    return posts

# def get_recent_posts(user):
#     """Get recent posts."""
#     query = """
#         SELECT postid, filename, owner, created
#         FROM posts
#         WHERE owner = ? OR owner IN
#         (SELECT username2 FROM following WHERE username1 = ?)
#         ORDER BY postid DESC;
#     """
#     return get_posts(query, (user, user))


def get_likes_count(postid):
    """Get like count."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(likeid) FROM likes WHERE postid = ?;",
                   (postid,))
    result = cursor.fetchone()
    connection = insta485.model.close_db("error")

    return result['COUNT(likeid)']


def get_comments_for_post(postid):
    """Get all the comments for each post."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT commentid, owner, text, created
        FROM comments
        WHERE postid = ?
        ORDER BY created ASC;
    """, (postid,))
    comments = cursor.fetchall()
    connection = insta485.model.close_db("error")
    return comments


def get_user_profile_picture(username):
    """Get URL of the profile picture of a specific user from the database."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT filename FROM users WHERE username = ?;",
                   (username,))
    profile_picture = cursor.fetchone()
    connection = insta485.model.close_db("error")

    return profile_picture['filename']


@insta485.app.route('/uploads/<filename>')
def serve_file(filename):
    """Serve a file."""
    # Check if the user is authenticated
    if "username" not in session:
        abort(403)  # Unauthenticated users get a 403 Forbidden error
    else:
        file_path = os.path.join(insta485.app.config['UPLOAD_FOLDER'],
                                 filename)

        # Check if the file exists
        if not os.path.exists(file_path):
            abort(404)

        # Serve the file using send_from_directory
        return send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                   filename)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if 'username' in flask.session:
        logged_in_user = flask.session['username']
    else:
        logged_in_user = "awdeorio"

    # Retrieve users not followed by the logged-in user
    users_not_followed = get_users_not_followed(logged_in_user)

    # Render the explore template
    return render_template('explore.html',
                           logname=logged_in_user,
                           users_not_followed=users_not_followed)


def get_users_not_followed(logged_in_user):
    """Retrieve users not followed by the logged-in user."""
    connection = insta485.model.get_db()
    cursor = connection.cursor()

    # Query users not followed by the logged-in user
    cursor.execute("""
        SELECT username, filename
        FROM users
        WHERE username != ? AND username NOT IN (
            SELECT username2 FROM following WHERE username1 = ?
        )
    """, (logged_in_user, logged_in_user))

    # Fetch all rows from the result
    users_not_followed = cursor.fetchall()

    # Close the database connection
    insta485.model.close_db("error")

    return users_not_followed
